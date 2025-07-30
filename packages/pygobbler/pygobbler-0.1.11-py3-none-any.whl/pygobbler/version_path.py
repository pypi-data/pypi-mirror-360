from . import fetch_directory


def version_path(project, asset, version, **kwargs) -> str:
    """
    Obtain the path to a versioned asset in the registry.

    Args:
        project:
            The name of the project.

        asset:
            The name of the asset of the ``project``.

        version:
            The name of the version of the ``asset`` to obtain.

        kwargs:
            Further arguments to :py:func:`~.fetch_directory`.

    Returns:
        The path to the directory containing the desired version.
    """
    return fetch_directory(project + "/" + asset + "/" + version, **kwargs)
