from typing import Optional, Tuple
import os
from . import allocate_upload_directory
from . import _utils as ut


def upload_directory(
    project: str,
    asset: str,
    version: str,
    directory: str,
    staging: str,
    url: str,
    probation: bool = False,
    consume: Optional[bool] = None,
    ignore_dot: bool = True,
    spoof: Optional[str] = None,
    concurrent: int = 1,
):
    """
    Upload a directory as a new versioned asset of a project in the registry.

    Args:
        project:
            The name of an existing project.

        asset:
            The name of a new or existing asset in ``project``.

        version:
            The name of a new version of ``asset``.

        directory:
            Path to a directory to be uploaded. For best performace, this
            should be a subdirectory of ``staging``, e.g., as created by
            :py:func:`~.allocate_upload_directory`.

        staging:
            Path to the staging directory.

        url:
            URL for the Gobbler REST API.

        probation:
            Whether to upload a probational version.
    
        consume:
            Whether the contents of ``directory`` can be consumed by the upload process.
            If true, the Gobbler will attempt to move files from ``directory`` into the registry.
            Otherwise, the contents of ``directory`` will not be modified by the upload.
            Defaults to true if the contents of ``directory`` need to be copied to ``staging``.

        ignore_dot:
            Whether to skip dotfiles in ``directory`` during upload.

        spoof:
            String containing the name of a user on whose behalf this request is being made.
            This should only be used if the Gobbler service allows spoofing by the current user. 
            If ``None``, no spoofing is performed.

        concurrent:
            Number of concurrent copies.
    """
    # Normalizing them so that they're comparable, in order to figure out whether 'directory' lies inside 'staging'.
    directory = os.path.normpath(directory)
    staging = os.path.normpath(staging)

    in_staging = False
    tmpd = directory
    while len(tmpd) > len(staging):
        tmpd = os.path.dirname(tmpd)
        if tmpd == staging:
            in_staging = True
            break

    purge_newdir = False 
    try:
        if not in_staging:
            newdir = allocate_upload_directory(staging) 

            # If we're copying everything to our own staging directory, we can
            # delete it afterwards without affecting the user. We do this
            # clean-up to free up storage in the staging space.
            purge_newdir = True 
            to_copy = []

            for root, dirs, files in os.walk(directory):
                for d in dirs:
                    src = os.path.join(root, d)
                    rel = os.path.relpath(src, directory)
                    os.mkdir(os.path.join(newdir, rel))

                for f in files:
                    src = os.path.join(root, f)
                    rel = os.path.relpath(src, directory)
                    dest = os.path.join(newdir, rel)

                    slink = ""
                    if os.path.islink(src):
                        slink = os.readlink(src)

                    if slink == "":
                        to_copy.append((src, dest))
                    else:
                        os.symlink(slink, dest)

            directory = newdir

            if concurrent == 1:
                for y in to_copy:
                    _transfer_file(y)
            else:
                import multiprocessing
                with multiprocessing.Pool(concurrent) as p:
                    p.map(_transfer_file, to_copy)

        if consume is None:
            # If we copied everything over to our own staging directory, we're entitled to consume its contents.
            consume = not in_staging

        req = {
            "source": os.path.basename(directory),
            "project": project,
            "asset": asset,
            "version": version,
            "on_probation": probation,
            "consume": consume,
            "ignore_dot": ignore_dot
        }
        ut.dump_request(staging, url, "upload", req, spoof=spoof)
        return

    finally:
        if purge_newdir:
            import shutil
            shutil.rmtree(newdir)


def _transfer_file(info: Tuple):
    src, dest = info
    import shutil
    shutil.copy(src, dest)

    sstat = os.stat(src)
    dstat = os.stat(dest)
    if sstat.st_size != dstat.st_size:
        raise ValueError("mismatch in sizes after copy (" + str(sstat.st_size) + " vs " + str(dstat.st_size) + ")")

    smd5 = compute_md5sum(src)
    dmd5 = compute_md5sum(src)
    if smd5 != dmd5:
        raise ValueError("mismatch in MD5 checksums after copy (" + str(smd5) + " vs " + str(dmd5) + ")")


def compute_md5sum(path: str):
    import hashlib
    hasher = hashlib.md5()
    with open(path, "rb") as handle:
        while True:
            chunk = handle.read(8192)
            if len(chunk) == 0:
                break
            hasher.update(chunk)
    return hasher.hexdigest()
