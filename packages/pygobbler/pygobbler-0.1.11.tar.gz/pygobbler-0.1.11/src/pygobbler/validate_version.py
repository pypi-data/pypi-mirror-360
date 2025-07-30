from . import _utils as ut


def validate_version(project: str, asset: str, version: str, staging: str, url: str):
    """
    Check the validity of a version of an asset of a project from the registry.
    This compares the size, MD5 checksums and link information in the internal ``..manifest`` and ``..links`` files to the contents of the directory in the registry.

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
        The requested version is validated.
    """
    ut.dump_request(staging, url, "validate_version", { "project": project, "asset": asset, "version": version })
