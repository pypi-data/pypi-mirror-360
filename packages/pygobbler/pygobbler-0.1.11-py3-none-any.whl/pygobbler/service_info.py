from typing import Dict, Any
import requests
from . import _utils as ut


def service_info(url: str) -> Dict[str, Any]:
    """
    Get information about the Gobbler service, namely the locations of the
    staging directory and registry.

    Args:
        url:
            URL of the gobbler REST API.

    Returns:
        Dictionary containing the location of the staging and registry
        directories.
    """
    res = requests.get(url + "/info")
    if res.status_code >= 300:
        raise ut.format_error(res)
    return res.json()
