from typing import Dict

#' @export
#' @importFrom utils tail
def unpack_path(path: str) -> Dict[str, str]:
    """Unpack a path to its combination of project, asset, version, and
    (optionally) path, for easier use in the various pygobbler functions.

    Args:
        path: 
            Relative path within the Gobbler registry. 

    Return:
        Dictionary with the ``project``, ``asset``, ``version`` and ``path`` keys.
        All values are strings except for ``path``, which may be None.
    """
    components = path.split("/")
    if len(components) < 3:
        raise ValueError("expected at least 3 path components in 'path'")

    if len(components) == 3 or components[3] == "":
        path = None
    else:
        path = "/".join(components[3:])

    return { "project": components[0], "asset": components[1], "version": components[2], "path": path }
