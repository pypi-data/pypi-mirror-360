# Changelog

## Version 0.1.11

- Modified `upload_directory()` to preserve empty directories and all symlinks when copying to the staging directory.
- Added options to `start_gobbler()` to set adminstrators and pass extra arguments to the Gobbler binary.
- Added a `dry_run=` option to `set_permissions()` for previewing the new permissions.

## Version 0.1.10

- Added the `validate_version()` function to validate an existing directory in the registry.
- Report empty subdirectories when listing directory contents with `list_files()`.
- Create empty subdirectories in `fetch_directory()` to completely reproduce the registry contents.

## Version 0.1.9

- Added spoofing options for the project owner-related endpoints, i.e., approving/rejecting probation, changing permissions, or uploading new versions.

## Version 0.1.8

- Delete request files from staging directory once each request is complete, to free up storage space on the backend.

## Version 0.1.7

- Bugfix to `force_remote=` in `list_projects()`, `list_assets()` and `list_versions()`.

## Version 0.1.6

- Added `create=` option to `allocate_upload_directory()` to only return a name without creating the directory.

## Version 0.1.5

- Added `consume=` option in `upload_directory()` to allow staging files to be moved into the registry.
- Added `ignore_dot=` option in `upload_directory()` to indicate whether dotfiles should be ignored.

## Version 0.1.4

- Added the `reroute_links()` function to support link rerouting.
- Respect process-level umask when creating temporary files in the staging directory.

## Version 0.1.3

- Enable setting/getting of asset-level permissions in `set_permissions()` and `fetch_permissions()`.
- Added the `force=` option to forcibly remove directories in `remove_asset()`, `remove_version()` and `reject_probation()`.
- Bugfix for handling relative links in `upload_directory()`.

## Version 0.1.2

- Added the `reindex_version()` function.

## Version 0.1.1

- Added `fetch_file()` utility to fetch individual files from the registry.
- Added the `global_write=` option to `set_permissions()` to enable global writes.
- Preserve relative links in the upload directory in `upload_directory()`. 
- Added an `unpack_path()` utility to return project/asset/version information from a path to a Gobbler resource.

## Version 0.1.0

- New release of the Gobbler.
