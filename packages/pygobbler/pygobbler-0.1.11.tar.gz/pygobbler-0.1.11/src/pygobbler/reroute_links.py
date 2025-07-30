from typing import List
from ._utils import dump_request


def reroute_links(to_delete: List, staging: str, url: str, dry_run: bool = False) -> List:
    """Reroute symbolic links to files in directories that are to be deleted, e.g., by :py:func:`~.remove_project`.
    This preserves the validity of links within the Gobbler registry.

    Note that rerouting does not actually delete the directories specified in ``to_delete``.
    Deletion requires separate invocations of :py:func:`~.remove_project` and friends - preferably after the user has verified that rerouting was successful!

    Rerouting is not necessary if ``to_delete`` consists only of probational versions, or projects/assets containing only probational versions.
    The Gobbler should never create links to files in probational version directories.

    Args:
        to_delete:
            List of projects, assets or versions to be deleted.
            Each entry should be a dicionary containing at least the ``project`` name.
            When deleting an asset, the inner list should contain an additional ``asset`` name.
            When deleting a version, the inner list should contain additional ``asset`` and ``version`` names.
            Different inner lists may specify different projects, assets or versions.

        staging:
            Path to the staging directory.

        url:
            URL for the Gobbler REST API.

        dry_run:
            Whether to perform a dry run of the rerouting.

    Returns:
        List of dictionaries.
        Each dictionary represents a rerouting action and contains the following fields.

        - ``path``, string containing the path to a symbolic link in the registry that was changed by rerouting.
        - ``copy``, boolean indicating whether the link at ``path`` was replaced by a copy of its target file.
          If ``False``, the link was merely updated to refer to a new target file.
        - ``source``, the path to the target file that caused rerouting of ``path``.
          Specifically, this is a file in one of the to-be-deleted directories specified in ``to_delete``.
          If ``copy = TRUE``, this is the original linked-to file that was copied to ``path``.

        If ``dry_run = False``, the registry is modified as described by the rerouting actions.
        Otherwise, no modifications are performed to the registry.
    """
    out = dump_request(staging, url, "reroute_links", { "to_delete": to_delete, "dry_run": dry_run })
    return out["changes"]
