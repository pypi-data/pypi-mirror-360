from typing import Optional, List
from . import _utils as ut


def create_project(project: str, staging: str, url: str, owners: Optional[List] = None, uploaders: Optional[List] = None):
    """
    Create a new project in the registry.

    Args:
        project:
            Name of the project to create.

        staging:
            Path to the staging directory.

        url:
            URL for the Gobbler REST API.

        owners:
            List of user IDs of the owners of this project. If not provided,
            the current user will be set as the sole owner.

        uploaders:
            List specifying the authorized uploaders for this project. See the
            ``uploaders`` field in :py:func:`~.fetch_permissions` return value
            for the expected format. 

    Returns:
        On success, the requested project is created in the registry.
    """

    req = { "project": project }

    permissions = {}
    if owners is not None:
        permissions["owners"] = owners

    if uploaders is not None:
        permissions["uploaders"] = uploaders

    if len(permissions):
        req["permissions"] = permissions

    ut.dump_request(staging, url, "create_project", req)
    return
