from . import _utils as ut


def remove_asset(project: str, asset: str, staging: str, url: str, force: bool = False):
    """
    Remove an asset of a project from the registry.
    This should only be performed by Gobbler instance administrators.
    Consider running :py:func:`~.reroute_links` beforehand to avoid dangling references to files in this asset.

    Args:
        project:
            The name of the project.

        asset:
            The name of the asset to remove.

        staging:
            Path to the staging directory.

        url:
            URL to the Gobbler REST API.

        force:
            Whether the asset should be forcibly removed if it contains invalid files.
            If this needs to be set to ``True``, users may need to call :py:func:`~.refresh_usage` afterwards to correct project-level usage statistics.
    """
    ut.dump_request(staging, url, "delete_asset", { "project": project, "asset": asset, "force": force })
