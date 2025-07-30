from typing import List
import requests
import os
from . import _utils as ut


def list_projects(registry: str, url: str, force_remote: bool = False) -> List[str]:
    """
    List all projects in the registry.

    Args:
        registry:
            Path to the registry.

        url:
            URL to the Gobbler REST API. Only used for remote access.

        force_remote:
            Whether to force remote access via the API, even if ``registry`` is
            on the same filesystem as the caller. 

    Returns:
        List of strings containing the project names.
    """
    listed = list_registry_directories(".", registry, url, force_remote)

    # Remove the ..logs directory.
    output = []
    for x in listed:
        if not x.startswith(".."):
            output.append(x)

    return output


def list_registry_directories(path: str, registry: str, url: str, force_remote: bool) -> List[str]:
    if not force_remote and os.path.exists(registry):
        output = []
        full = os.path.join(registry, path)
        for x in os.listdir(full):
            if os.path.isdir(os.path.join(full, x)):
                output.append(x)
        return output

    else:
        url += "/list"
        if path != ".":
            import urllib
            url += "?path=" + urllib.parse.quote_plus(path)

        req = requests.get(url)
        if req.status_code >= 300:
            raise ut.format_error(req)

        listing = req.json()
        output = []
        for x in listing:
            if x.endswith("/"):
                output.append(x[:-1])

        return output
