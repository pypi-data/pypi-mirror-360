from .event_forwarder import EventForwarder
from ..event_translators.leef_translator import LeefTranslator
from ..syslog_client import SyslogClient


class QRadarEventForwarder(EventForwarder):
    """
    Lookout's QRadar plugin utilizes a syslog connection to forward events for ingestion.
    """

    def __init__(self, qradar_address):
        self.qradar_address = qradar_address
        self.event_translator = LeefTranslator(mra_v2=True)
        self.syslog_client = SyslogClient(
            "MRAv2SyslogClient",
            self.event_translator.formatEvent,
            self.qradar_address,
        )

    # TODO: handle syslog stale client thing
    def write(self, event: dict, _entName: str):
        """
        Write a MRA v2 event to QRadar

        Args:
            event (dict): MRA v2 event

        JIRA: EMM-8312: Events stop appearing in QRadar if there has been long (~15 minute)
        break between events
        """
        self.syslog_client.write(event)
