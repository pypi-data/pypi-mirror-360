import os
from .fetch_manifest import fetch_manifest


def clone_version(project: str, asset: str, version: str, destination: str, registry: str):
    """
    Clone the directory structure for a versioned asset into a separate location.
    This is typically used to prepare a new version for a lightweight upload.

    More specifically, cloning involves creating a directory at ``destination``
    that has the same structure as that of the specified project-asset-version.
    All files in the version are represented as symlinks from ``destination``
    to the corresponding file in the ``registry``.The idea is that, when
    ``destination`` is used in :py:func:`~.upload_directory`, the symlinks are
    converted into upload links. This allows users to create new versions very
    cheaply as duplicate files are not stored in the backend.

    Users can more-or-less do whatever they want inside the cloned ``destination``,
    but the symlink targets should be read-only as they refer to immutable files in
    the ``registry``.  If a file in ``destination`` needs to be modified, the
    symlink should be deleted and replaced with a new file.

    Args:
        project:
            The name of the project.

        asset:
            The name of the asset of the ``project``.

        version:
            The name of the version of the ``asset`` to clone.

        destination:
            Path to a destination directory at which to create the clone.

        registry: 
            Path to the registry.
    """
    target = os.path.join(registry, project, asset, version)
    listing = fetch_manifest(project, asset, version, registry=registry, url=None)
    os.makedirs(destination, exist_ok=True)
    for x in listing.keys():
        dpath = os.path.join(destination, x)
        os.makedirs(os.path.dirname(dpath), exist_ok=True)
        os.symlink(os.path.join(target, x), dpath)
    return
