import logging, json, argparse, datetime, time, socket

from logging.handlers import RotatingFileHandler

from lookout_mra_client.event_forwarders.event_forwarder import EventForwarder
from lookout_mra_client.event_store.event_store import EventStore
from lookout_mra_client.event_store.file_event_store import FileEventStore
from lookout_mra_client.mra_v2_stream_thread import MRAv2StreamThread
from lookout_mra_client.lookout_logger import init_lookout_logger
from lookout_mra_client.syslog_client import SyslogClient


FILE_FORWARDER = "file"
SYSLOG_FORWARDER = "syslog"


class FileEventForwarder(EventForwarder):
    def __init__(
        self, filename: str, event_store: EventStore, maxMegabytes: int = 10, backupCount: int = 5
    ):
        self.logger = logging.getLogger("FileEventForwarder")
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False

        maxBytes = maxMegabytes * 1e6
        file_handler = RotatingFileHandler(filename, maxBytes=maxBytes, backupCount=backupCount)
        file_handler.formatter = logging.Formatter("%(message)s")

        self.logger.addHandler(file_handler)
        self.event_store = event_store

    def write(self, event: dict, entName: str = ""):
        event["entName"] = entName
        self.logger.info(json.dumps(event) + "\r\n")
        if event["id"]:
            self.event_store.received_event(event["id"])


class SyslogEventForwarder(EventForwarder):
    def __init__(self, syslog_address: str, event_store: EventStore) -> None:
        self.syslog_client = SyslogClient(
            "MRAv2SyslogClient", lambda d: str(d), (syslog_address, 514), True, socket.SOCK_DGRAM
        )
        self.event_store = event_store

    def write(self, event: dict, entName: str = ""):
        event["entName"] = entName
        self.syslog_client.write(event)
        if event["id"]:
            self.event_store.received_event(event["id"])


def start_thread(key_filename: str, event_type: list, args) -> None:
    init_lookout_logger("./mra_v2_demo_script.log")

    store = FileEventStore(args.event_store)
    last_event = store.load()
    stream_checkpoint = {}
    if not last_event:
        start_time = datetime.datetime.now() - datetime.timedelta(days=1)
        start_time = start_time.replace(tzinfo=datetime.timezone.utc)
        stream_checkpoint["start_time"] = start_time
    else:
        stream_checkpoint["last_event_id"] = last_event

    if args.forwarder == FILE_FORWARDER:
        forwarder = FileEventForwarder(args.output, store)
    elif args.forwarder == SYSLOG_FORWARDER:
        forwarder = SyslogEventForwarder(args.address, store)
    else:
        print(f"Unknown event forwarder: {args.forwarder}")
        exit(0)

    key_file = open(key_filename, "r")
    api_key = key_file.read().strip()

    stream_args = {
        "api_domain": "https://api.lookout.com",
        "api_key": api_key,
        "event_type": ",".join(event_type),
        **stream_checkpoint,
        "user_agent": "MRAv2ClientDemo",
    }
    mra = MRAv2StreamThread("demoEnt", forwarder, **stream_args)

    try:
        mra.start()
        while True:
            time.sleep(100)
    except KeyboardInterrupt:
        mra.shutdown_flag.set()
        mra.join()
        print("\nGoodbye :)")
    finally:
        if mra and mra.stream and mra.stream.last_event_id:
            store.save(mra.stream.last_event_id)


def get_parser() -> argparse.ArgumentParser:
    example_text = f"""example:
  %(prog)s file \\
    --output /var/log/output.txt \\
    --api_key /var/opt/apikey.txt \\
    --event_type THREAT DEVICE

  %(prog)s syslog \\
    --api_key /var/opt/apikey.txt \\
    --event_type THREAT DEVICE
    
  %(prog)s syslog \\
    --address xxx.xxx.xxx.xxx \\
    --api_key /var/opt/apikey.txt \\
    --event_type THREAT DEVICE"""

    parser = argparse.ArgumentParser(
        description="Demonstrate MRAv2 event streams in python",
        epilog=example_text,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument("--api_key", required=True, help="Path of api key file.")
    common_parser.add_argument(
        "--event_type",
        help="MRA event types to retrieve, i.e. THREAT, DEVICE, AUDIT.",
        nargs="+",
        default=[],
    )
    common_parser.add_argument("--event_store", required=True, help="Path of event store file")

    subparsers = parser.add_subparsers(title="forwarders", dest="forwarder", required=True)

    file_args_desc = "Output events to a given file path"
    file_args = subparsers.add_parser(
        "file", help=file_args_desc, description=file_args_desc, parents=[common_parser]
    )
    file_args.add_argument("--output", required=True, help="Output file to write events to.")

    syslog_args_desc = "Output events to a local/remote syslog server"
    syslog_args = subparsers.add_parser(
        "syslog", help=syslog_args_desc, description=syslog_args_desc, parents=[common_parser]
    )
    syslog_args.add_argument("--address", help="IP address of syslog server", default="localhost")

    return parser


def main():
    args = get_parser().parse_args()
    start_thread(args.api_key, args.event_type, args)
