from typing import Optional
import os
from .fetch_directory import _local_registry, _acquire_file_raw


def fetch_file(path: str, registry: str, url: str, cache: Optional[str] = None, force_remote: bool = False, overwrite: bool = False) -> str:
    """
    Obtain the path to a file in the registry. This may create a local copy if
    the caller is not on the same filesystem as the registry.

    Args:
        path: 
            Relative path to a file within the registry. This usually takes the
            form of ``PROJECT/ASSET/VERSION/*``.

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
        Path to the file on the caller's filesystem.  This is either a path to
        the file in the registry if it is accessible, or a path to a local
        cache of the registry's contents otherwise.
    """
    if not force_remote and os.path.exists(registry):
        return os.path.join(registry, path)
    cache = _local_registry(cache, url)
    return _acquire_file_raw(cache, path, url=url, overwrite=overwrite)
