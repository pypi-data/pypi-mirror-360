from typing import Optional
import os
import json
import requests
from . import _utils as ut


def fetch_latest(project: str, asset: str, registry: str, url: str, force_remote: bool = False) -> Optional[str]:
    """
    Fetch the latest version of an asset of a project.

    Args:
        project:
            Name of a project.

        asset:
            Name of an asset in the ``project``.

        registry:
            Path to the Gobbler registry.

        url:
            URL of the REST API. Only used for remote queries.

        force_remote:
            Whether to force a remote query via ``url``, even if the
            ``registry`` is present on the current filesystem.

    Returns:
        The name of the latest version of the ``asset``, or None if
        no latest version exists.
    """
    if os.path.exists(registry) and not force_remote:
        proposed = os.path.join(registry, project, asset, "..latest")
        if not os.path.exists(proposed):
            return None
        with open(proposed, "r") as handle:
            vers = json.load(handle)
        return vers["version"]

    res = requests.get(url + "/fetch/" + project + "/" + asset + "/..latest")
    if res.status_code == 404:
        return None
    elif res.status_code >= 300:
        raise ut.format_error(res)
    body = res.json()
    return body["version"]
