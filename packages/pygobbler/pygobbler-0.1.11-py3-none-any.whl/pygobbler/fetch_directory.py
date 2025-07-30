from typing import Optional
import os
import tempfile
import urllib
import requests
import shutil
from . import _utils as ut


def _local_registry(cache: Optional[str], url: str) -> str:
    if cache is None:
        import appdirs
        cache = appdirs.user_data_dir("gobbler", "aaron")
    return os.path.join(cache, urllib.parse.quote_plus(url))


def _acquire_file_raw(cache: str, path: str, url: str, overwrite: bool) -> str:
    target = os.path.join(cache, "REGISTRY", path)

    if overwrite or not os.path.exists(target):
        tempdir = os.path.join(cache, "TEMP")
        os.makedirs(tempdir, exist_ok=True)
        os.makedirs(os.path.dirname(target), exist_ok=True)

        tempfid, temppath = tempfile.mkstemp(dir=tempdir)
        try:
            with requests.get(url + "/fetch/" + path, stream=True) as r:
                if r.status_code >= 300:
                    raise ut.format_error(r)
                with os.fdopen(tempfid, 'wb') as f:
                    shutil.copyfileobj(r.raw, f)
            os.rename(temppath, target) # this should be more or less atomic, so no need for locks.
        finally:
            try:
                os.remove(temppath)
            except:
                pass

    return target


def _acquire_file(cache: str, path: str, name: str, url: str, overwrite: bool) -> str:
    return _acquire_file_raw(cache, path + "/" + name, url, overwrite)


def fetch_directory(path: str, registry: str, url: str, cache: Optional[str] = None, force_remote: bool = False, overwrite: bool = False, concurrent: int = 1) -> str:
    """
    Obtain the path to a directory in the registry. This may create a local
    copy of the subdirectory's contents if the caller is not on the same
    filesystem as the registry.

    Args:
        path: 
            Relative path to a subdirectory within the registry. This usually
            takes the form of ``PROJECT/ASSET/VERSION/*``.

        registry:
            Path to the registry.

        url:
            URL to the Gobbler REST API. Only used for remote queries.

        cache:
            Path to a cache directory. If None, an appropriate location is
            automatically chosen. Only used for remote access.

        force_remote:
            Whether to force remote access. This will download all files in the
            ``path`` via the REST API and cache them locally, even if
            ``registry`` is present on the same filesystem.

        overwrite:
            Whether to overwrite existing files in the cache.

        concurrent:
            Number of concurrent downloads.

    Returns:
        Path to the subdirectory on the caller's filesystem.  This is either a
        path to the registry if it is accessible, or a path to a local cache of
        the registry's contents otherwise.
    """
    if not force_remote and os.path.exists(registry):
        return os.path.join(registry, path)

    cache = _local_registry(cache, url)
    final = os.path.join(cache, "REGISTRY", path)
    ok = os.path.join(cache, "SUCCESS", path, "....OK")
    if not overwrite and os.path.exists(ok) and os.path.exists(final):
        return final

    res = requests.get(url + "/list?path=" + urllib.parse.quote_plus(path) + "&recursive=true")
    if res.status_code >= 300:
        raise ut.format_error(res)
    raw_listing = res.json()

    listing = []
    for f in raw_listing:
        if f.endswith("/"):
            epath = os.path.join(final, f)
            if not os.path.isdir(epath):
                os.makedirs(epath, exist_ok=True)
        else:
            listing.append(f)

    if concurrent == 1:
        for y in listing:
            _acquire_file(cache, name=y, path=path, url=url, overwrite=overwrite)
    else:
        import multiprocessing
        import functools
        with multiprocessing.Pool(concurrent) as p:
            p.map(functools.partial(_acquire_file, cache, path, url=url, overwrite=overwrite), listing)

    # We use a directory-level OK file to avoid having to scan through all 
    # the directory contents to indicate that it's complete.
    os.makedirs(os.path.dirname(ok), exist_ok=True)
    with open(ok, "w") as handle:
        handle.write("")
    return final
