from . import _utils as ut


def remove_version(project: str, asset: str, version: str, staging: str, url: str, force: bool = False):
    """
    Remove a version of a project asset from the registry.
    This should only be performed by Gobbler instance administrators.
    Consider running :py:func:`~.reroute_links` beforehand to avoid dangling references to files in this version.

    Args:
        project:
            The name of the project.

        asset:
            The name of the asset of the ``project``.

        version:
            The name of the version of the ``asset`` to remove.

        staging:
            Path to the staging directory.

        force:
            Whether the version should be forcibly removed if it contains invalid files.
            If this needs to be set to ``True``, users may need to call :py:func:`~.refresh_usage` afterwards to correct project-level usage statistics.
            Similarly, :py:func:`~.refresh_latest` may also need to be called.

        url:
            URL to the Gobbler REST API.
    """
    ut.dump_request(staging, url, "delete_version", { "project": project, "asset": asset, "version": version, "force": force })
