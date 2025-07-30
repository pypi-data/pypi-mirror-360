from typing import Optional, List
import os
import requests
from . import _utils as ut


def list_files(project: str, asset: str, version: str, registry: str, url: str, prefix: Optional[str] = None , include_dotdot: bool = True, force_remote: bool = False) -> List[str]:
    """
    List the contents of a version of a project asset.

    Args:
        project:
            The name of the project.

        asset:
            The name of the asset in ``project``.

        version:
            The name of the version of the ``asset``.

        registry:
            Path to the registry.

        url:
            URL to the Gobbler REST API. Only used for remote access.

        prefix:
            Prefix for the path within this version's subdirectory. If
            provided, files are only listed if they have a relative path (i.e.,
            inside the version subdirectory) that starts with this prefix. If
            None, all files associated with this version are listed.

        include_dotdot:
            Whether to list files with path components that start with ``..``.

        force_remote:
            Whether to force remote access via the API, even if ``registry`` is
            on the same filesystem as the caller. 

    Returns:
        List of strings containing the relative paths of files associated with
        the versioned asset. All paths will start with ``prefix`` if provided.
    """
    suffix_filter = None
    if prefix is not None:
        if prefix.endswith("/"):
            prefix = prefix[:-1]
        else:
            suffix_filter = os.path.basename(prefix)
            prefix = os.path.dirname(prefix)
            if prefix == "":
                prefix = None

    listing = []

    if not force_remote and os.path.exists(registry):
        target = os.path.join(registry, project, asset, version)
        if prefix is not None:
            target = os.path.join(target, prefix)

        empty_directories = {}
        for root, dirs, files in os.walk(target):
            rel = os.path.relpath(root, target)
            for f in files:
                if include_dotdot or not f.startswith(".."):
                    if rel != ".":
                        f = os.path.join(rel, f)
                    listing.append(f)
            for d in dirs:
                if rel != ".":
                    d = os.path.join(rel, d)
                empty_directories[d] = True

        for f in listing:
            fdir = os.path.dirname(f)
            if fdir != ".":
                empty_directories[fdir] = False
        for d, empty in empty_directories.items():
            if empty:
                ddir = os.path.dirname(d)
                if ddir != ".":
                    empty_directories[ddir] = False
        for d, empty in empty_directories.items():
            if empty:
                listing.append(d + "/")

    else:
        target = project + "/" + asset + "/" + version
        if prefix is not None:
            target += "/" + prefix

        import urllib
        res = requests.get(url + "/list?path=" + urllib.parse.quote_plus(target) + "&recursive=true")
        if res.status_code >= 300:
            raise ut.format_error(res)

        listing = res.json()

    if not include_dotdot:
        listing = filter(lambda x : not x.startswith("..") and x.find("/..") == -1, listing)

    if suffix_filter is not None:
        listing = filter(lambda x : x.startswith(suffix_filter), listing)

    if prefix is not None:
        for i, x in enumerate(listing):
            listing[i] = prefix + "/" + x

    return listing
