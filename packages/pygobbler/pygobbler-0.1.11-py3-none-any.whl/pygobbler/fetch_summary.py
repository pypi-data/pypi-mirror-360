from typing import Optional, Dict, Any
import os
import json
from . import fetch_directory as fd


def fetch_summary(project: str, asset: str, version: str, registry: str, url: str, cache: Optional[str] = None, force_remote: bool = False, overwrite: bool = False) -> Dict[str, Any]:
    """
    Fetch the summary for a particular version of a project asset.

    Args:
        project:
            Name of a project.

        asset:
            Name of an asset in the ``project``.

        version:
            Name of a version of the ``asset``.

        registry:
            Path to the Gobbler registry.

        url:
            URL of the REST API. Only used for remote queries.

        cache:
            Path to a cache directory. If None, a default cache location is
            selected. Only used for remote queries.

        force_remote:
            Whether to force a remote query via ``url``, even if the
            ``registry`` is present on the current filesystem.

        overwrite:
            Whether to overwrite existing entries in the cache. Only used for
            remote queries.

    Returns:
        Dictionary containing summary information including:

        - ``uploader_user_id``, string containing the UID of the uploading user.
        - ``upload_start_time``, string containing the upload start time in
          Internet Date/Time format.
        - ``upload_finish_time``, string containing the upload finish time in
          Internet Date/Time format.
        - ``on_probation`` (optional), boolean indicating whether this version of
          the asset is a probational upload.
    """

    if not force_remote and os.path.exists(registry):
        path = os.path.join(registry, project, asset, version, "..summary")
    else:
        cache = fd._local_registry(cache, url)
        path = fd._acquire_file(cache, project + "/" + asset + "/" +  version, "..summary", url=url, overwrite=overwrite)

    with open(path, "r") as handle:
        out = json.load(handle)
    return out
