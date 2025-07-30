from typing import Optional, Dict, Any
import os
import json
from . import fetch_directory as fd


def fetch_manifest(project: str, asset: str, version: str, registry: str, url: str, cache: Optional[str] = None, force_remote: bool = False, overwrite: bool = False) -> Dict[str, Any]:
    """
    Fetch the manifest for a version of a project asset.

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
        Dictionary containing the manifest. Each key is a relative path to a
        file in this version of the project asset, and each value is a
        dictionary with the following fields:

        - ``size``, integer specifying the size of the file in bytes.
        - ``md5sum``, string containing the file's hex-encoded MD5 checksum.
        - ``link`` (optional): a list specifying the link destination for a
          file. This contains the strings ``project``, ``asset``,
          ``version`` and ``path``; if the link destination is also a link,
          an ``ancestor`` dictionary will be present containing the final
          location of the file after resolving all intermediate links. 
    """
    if not force_remote and os.path.exists(registry):
        path = os.path.join(registry, project, asset, version, "..manifest")
    else:
        cache = fd._local_registry(cache, url)
        path = fd._acquire_file(cache, project + "/" + asset + "/" + version, "..manifest", url=url, overwrite=overwrite)

    with open(path, "r") as handle:
        out = json.load(handle)
    return out
