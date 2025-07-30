import sys

if sys.version_info[:2] >= (3, 8):
    # TODO: Import directly (no need for conditional) when `python_requires = >= 3.8`
    from importlib.metadata import PackageNotFoundError, version  # pragma: no cover
else:
    from importlib_metadata import PackageNotFoundError, version  # pragma: no cover

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = __name__
    __version__ = version(dist_name)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError

from .start_gobbler import start_gobbler, stop_gobbler
from .create_project import create_project
from .fetch_permissions import fetch_permissions
from .fetch_latest import fetch_latest
from .fetch_summary import fetch_summary
from .fetch_manifest import fetch_manifest
from .fetch_usage import fetch_usage
from .fetch_file import fetch_file
from .fetch_directory import fetch_directory
from .allocate_upload_directory import allocate_upload_directory
from .upload_directory import upload_directory
from .list_projects import list_projects
from .list_assets import list_assets
from .list_versions import list_versions
from .list_files import list_files
from .remove_project import remove_project
from .remove_asset import remove_asset
from .remove_version import remove_version
from .clone_version import clone_version
from .reindex_version import reindex_version
from .validate_version import validate_version
from .service_info import service_info
from .version_path import version_path
from .refresh_latest import refresh_latest
from .refresh_usage import refresh_usage
from .approve_probation import approve_probation
from .reject_probation import reject_probation
from .set_permissions import set_permissions
from .unpack_path import unpack_path
from .reroute_links import reroute_links
