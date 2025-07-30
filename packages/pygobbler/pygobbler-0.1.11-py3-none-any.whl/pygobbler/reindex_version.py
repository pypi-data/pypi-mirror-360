from . import _utils as ut


def reindex_version(project: str, asset: str, version: str, staging: str, url: str):
    """
    Reindex a version of a project asset in the registry.
    This regenerates all of the internal ``..manifest`` and ``..links`` files.

    Args:
        project:
            The name of the project.

        asset:
            The name of the asset of the ``project``.

        version:
            The name of the version of the ``asset`` to remove.

        staging:
            Path to the staging directory.

        url:
            URL to the Gobbler REST API.

    Returns:
        The requested version is reindexed.
    """
    ut.dump_request(staging, url, "reindex_version", { "project": project, "asset": asset, "version": version })
