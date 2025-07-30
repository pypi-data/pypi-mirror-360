from typing import Dict, Any, Optional
import os
import json
import requests
from . import _utils as ut


def fetch_permissions(
    project: str,
    registry: str,
    url: str,
    asset: Optional[str] = None,
    force_remote: bool = False,
) -> Dict[str, Any]:
    """
    Fetch permissions for a project.

    Args:
        project:
            Name of a project.

        registry:
            Path to the Gobbler registry.

        url:
            URL to the Gobbler REST API.
            Only used for remote queries.

        asset:
            Name of the asset inside the project.
            If supplied, permissions are returned for this asset rather than the entire project.

        force_remote:
            Whether to force a remote query via ``url``, even if the ``registry`` is present on the current filesystem.

    Returns:
        A dictionary containing the permissions for the ``project``.
        This contains ``owners``, a list of strings with the user IDs of the owners of this project;
        and ``uploaders``, a list of dictionaries where each dictionary has the following fields:

        - ``id``, string containing a user ID that is authorized to upload.
        - ``asset`` (optional), string containing the name of the asset that the uploader is allowed to upload to.
          If not present, there is no restriction on the uploaded asset name.
        - ``version`` (optional), string containing the name of the version that the uploader is allowed to upload to.
          If not present, there is no restriction on the uploaded version name.
        - ``until`` (optional), string containing the expiry date of this authorization in Internet Date/Time format.
          If not provided, the authorization does not expire.
        - ``trusted`` (optional), a boolean indicating whether the uploader is trusted.
          If not provided, defaults to ``False``.

        When ``asset = None``, the dictionary may also contain `global_write`, a boolean indicating whether global writes are supported.
        If ``True``, any user may create a new asset in this project, and each user can upload new versions to any asset they created under this mode.

        If ``asset`` is provided, the returned dictionary contains ``owners`` and ``uploaders`` to describe the owners and uploaders, respectively, for the specified ``asset``.
    """
    use_registry = (os.path.exists(registry) and not force_remote)

    if asset is None:
        if use_registry:
            with open(os.path.join(registry, project, "..permissions"), "r") as f:
                perms = json.load(f)
        else:
            res = requests.get(url + "/fetch/" + project + "/..permissions")
            if res.status_code >= 300:
                raise ut.format_error(res)
            perms = res.json()

    else:
        perms = { "owners": [], "uploaders": [] }
        if use_registry:
            ppath = os.path.join(registry, project, asset, "..permissions")
            if os.path.exists(ppath):
                with open(ppath, "r") as f:
                    perms = json.load(f)
        else:
            res = requests.get(url + "/fetch/" + project + "/" + asset + "/..permissions")
            if res.status_code != 404:
                if res.status_code >= 300:
                    raise ut.format_error(res)
                perms = res.json()

    return perms
