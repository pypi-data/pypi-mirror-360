from . import _utils as ut


def remove_project(project: str, staging: str, url: str):
    """
    Remove a project from the registry.
    This should only be performed by Gobbler instance administrators.
    Consider running :py:func:`~.reroute_links` beforehand to avoid dangling references to files in this project.

    Args:
        project:
            String containing the project to remove.

        staging:
            Path to the staging directory.

        url:
            URL for the Gobbler REST API.
    """
    ut.dump_request(staging, url, "delete_project", { "project": project })
