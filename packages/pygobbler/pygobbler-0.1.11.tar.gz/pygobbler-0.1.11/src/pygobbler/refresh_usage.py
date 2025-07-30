from . import _utils as ut


def refresh_usage(project: str, staging: str, url:str) -> int:
    """
    Recompute the quota usage of a project. This is useful on rare occasions
    where multiple simultaneous uploads cause the usage calculations to be out
    of sync.

    Args:
        project:
            Name of the project.

        staging:
            Path to the staging directory.

        url:
            URL of the gobbler REST API.

    Returns:
        Total quota usage of this project, in bytes.
    """
    resp = ut.dump_request(staging, url, "refresh_usage", { "project": project })
    return resp["total"]
