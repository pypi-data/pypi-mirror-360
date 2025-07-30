from importlib.metadata import version, PackageNotFoundError


def __get_version():
    """
    importlib.metadata works when lookout_mra_client is installed as a package, but not
    when running tests.
    """
    try:
        return version("lookout_mra_client")
    except PackageNotFoundError:
        return "Unknown"


__version__ = __get_version()
__prj_name__ = f"lookout-mra-client/{__version__}"
