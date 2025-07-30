from typing import Optional
from . import _utils as ut


def refresh_latest(project: str, asset: str, staging: str, url:str) -> Optional[str]:
    """
    Recompute the latest version of a project's asset. This is useful on rare
    occasions where multiple simultaneous uploads cause the latest version to
    be slightly out of sync.

    Args:
        project:
            Name of the project.

        asset:
            Name of the asset.

        staging:
            Path to the staging directory.

        url:
            URL of the gobbler REST API.

    Returns:
        Latest version of the project, or None if there is no non-probational version.
    """
    resp = ut.dump_request(staging, url, "refresh_latest", { "project": project, "asset": asset })
    if "version" in resp:
        return resp["version"]
    else:
        return None
