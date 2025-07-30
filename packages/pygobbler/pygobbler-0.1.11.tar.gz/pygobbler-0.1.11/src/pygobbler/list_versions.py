from typing import List
from .list_projects import list_registry_directories


def list_versions(project: str, asset: str, registry: str, url: str, force_remote: bool = False) -> List[str]:
    """
    List all versions of a project asset.

    Args:
        project:
            The name of the project.

        asset:
            The name of the asset in ``project``.

        registry:
            Path to the registry.

        url:
            URL to the Gobbler REST API. Only used for remote access.

        force_remote:
            Whether to force remote access via the API, even if ``registry`` is
            on the same filesystem as the caller. 

    Returns:
        List of strings containing the project names.
    """
    return list_registry_directories(project + "/" + asset, registry, url, force_remote)
