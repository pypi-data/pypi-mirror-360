from typing import Optional

from . import _utils as ut


def reject_probation(project: str, asset: str, version: str, staging: str, url: str, force: bool = False, spoof: Optional[str] = None):
    """
    Reject a probational upload of a version of a project's asset.

    Args:
        project:
            The name of the project.

        asset:
            The name of the asset of the ``project``.

        version:
            The name of the version of the ``asset`` to reject.

        staging:
            Path to the staging directory.

        url:
            URL to the Gobbler REST API.

        force:
            Whether the version should be forcibly rejected and removed if it contains invalid files.
            If this needs to be set to ``True``, users may need to call :py:func:`~.refresh_usage` afterwards to correct project-level usage statistics.

        spoof:
            String containing the name of a user on whose behalf this request is being made.
            This should only be used if the Gobbler service allows spoofing by the current user. 
            If ``None``, no spoofing is performed.
    """
    ut.dump_request(staging, url, "reject_probation", { "project": project, "asset": asset, "version": version, "force": force }, spoof=spoof)
