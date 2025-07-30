from typing import Optional
import os
import json
import requests
from . import _utils as ut


def fetch_usage(project: str, registry: str, url: str, force_remote: bool = False) -> Optional[str]:
    """
    Fetch the disk usage of a project.

    Args:
        project:
            Name of a project.

        registry:
            Path to the Gobbler registry.

        url:
            URL of the REST API.

        force_remote:
            Whether to force a remote query via ``url``, even if the
            ``registry`` is present on the current filesystem.

    Returns:
        The current usage (in bytes) for this project.
    """
    if os.path.exists(registry) and not force_remote:
        proposed = os.path.join(registry, project, "..usage")
        with open(proposed, "r") as handle:
            used = json.load(handle)
        return used["total"]

    res = requests.get(url + "/fetch/" + project + "/..usage")
    if res.status_code >= 300:
        raise ut.format_error(res)
    body = res.json()
    return body["total"]
