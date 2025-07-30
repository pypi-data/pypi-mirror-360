import os
import tempfile


def allocate_upload_directory(staging: str, create: bool = True) -> str:
    """
    Allocate a subdirectory in the staging directory to prepare files for upload via :py:func:`~.upload_directory`.

    Args:
        staging:
            Path to the staging directory.

        create:
            Whether to actually create the subdirectory.

    Returns:
        Path to a new subdirectory for staging uploads.
        If ``create = False``, a name is chosen but the subdirectory is not created.
    """
    trial = tempfile.mkdtemp(dir=staging)

    # Doing this little shuffle to get the right permissions. tempfile loves to
    # create 0o700 directories that the gobbler service account can't actually
    # read, so we just delete it and create it again under the more permissive
    # umask. Unfortunately we can't use chmod as this screws up FACLs.
    os.rmdir(trial)

    if create:
        os.mkdir(trial)
    return trial
