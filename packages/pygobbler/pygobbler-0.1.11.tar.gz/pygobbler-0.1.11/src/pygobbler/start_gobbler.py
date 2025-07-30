from typing import Optional, Tuple
import tempfile
import requests
import os
from . import _utils as ut

test_staging = None
test_registry = None
test_port = None
test_process = None

def start_gobbler(
    staging: Optional[str] = None,
    registry: Optional[str] = None,
    port: Optional[int] = None,
    wait: float = 1,
    version: str = "0.5.0",
    overwrite: bool = False,
    admin: Optional[list] = None, 
    extra_args: list = [],
) -> Tuple[bool, str, str, str]:
    """
    Start a test Gobbler service.

    Args:
        registry: 
            Path to a registry directory. If None, a temporary directory is
            automatically created.

        staging: 
            Path to a registry directory. If None, a temporary directory is
            automatically created.

        port:
            Port number for the Gobbler API to receive requests. If None, an
            open port is automatically chosen.

        wait:
            Number of seconds to wait for the service to initialize before use.

        version:
            Version of the service to run.

        overwrite:
            Whether to overwrite the existing Gobbler binary.

        admin:
            List of strings containing the user names of the Gobbler administrators.
            If ``None``, the current user is used.

        extra_args:
            Additional arguments to pass to the Gobbler service on the command line.

    Returns:
        A tuple indicating whether a new test service was created (or an
        existing instance was re-used), the path to the staging directory, the
        path to the registry, and the chosen URL. If a service is already
        running, this function is a no-op and the configuration details of the
        existing service will be returned.
    """
    global test_staging
    global test_registry
    global test_process
    global test_port

    if test_process is not None:
        return False, test_staging, test_registry, "http://0.0.0.0:" + str(test_port)

    exe = _acquire_gobbler_binary(version, overwrite)
    _initialize_gobbler_process(exe, staging, registry, port, admin, extra_args)

    import time
    time.sleep(wait) # give it some time to spin up.
    return True, test_staging, test_registry, "http://0.0.0.0:" + str(test_port)


def _acquire_gobbler_binary(version: str, overwrite: bool):
    import platform
    sysname = platform.system()
    if sysname == "Darwin":
        OS = "darwin"
    elif sysname == "Linux":
        OS = "linux"
    else:
        raise ValueError("unsupported operating system '" + sysname + "'")

    sysmachine = platform.machine()
    if sysmachine == "arm64":
        arch = "arm64"
    elif sysmachine == "x86_64":
        arch = "amd64"
    else:
        raise ValueError("unsupported architecture '" + sysmachine + "'")

    import appdirs
    cache = appdirs.user_data_dir("gobbler", "aaron")
    desired = "gobbler-" + OS + "-" + arch
    exe = os.path.join(cache, desired + "-" + version)

    if not os.path.exists(exe) or overwrite:
        import shutil
        url = "https://github.com/ArtifactDB/gobbler/releases/download/" + version + "/" + desired

        os.makedirs(cache, exist_ok=True)
        tmp = exe + ".tmp"
        with requests.get(url, stream=True) as r:
            if r.status_code >= 300:
                raise ut.format_error(r)
            with open(tmp, 'wb') as f:
                shutil.copyfileobj(r.raw, f)

        os.chmod(tmp, 0o755)

        # Using a write-and-rename paradigm to provide some atomicity. Note
        # that renaming doesn't work across different filesystems so in that
        # case we just fall back to copying.
        try:
            shutil.move(tmp, exe)
        except:
            shutil.copy(tmp, exe)

    return exe
   

def _initialize_gobbler_process(exe: str, staging: Optional[str], registry: Optional[str], port: Optional[int], admin: Optional[str], extra_args: list):
    if staging is None:
        staging = tempfile.mkdtemp()
    global test_staging
    test_staging = staging

    if registry is None:
        registry = tempfile.mkdtemp()
    global test_registry
    test_registry = registry

    if port is None:
        import socket
        with socket.socket(socket.AF_INET) as s:
            s.bind(('0.0.0.0', 0))
            port = s.getsockname()[1]
    global test_port
    test_port = port

    if admin is None:
        import getpass
        admin = [getpass.getuser()]

    cmd_args = [
        exe,
        "-registry", registry,
        "-staging", staging,
        "-port", str(port) 
    ]
    if len(admin) > 0:
        cmd_args += [ "-admin", ",".join(admin) ]
    cmd_args += extra_args

    import subprocess
    global test_process
    test_process = subprocess.Popen(cmd_args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    import atexit
    atexit.register(stop_gobbler)
    return


def stop_gobbler():
    """
    Stop any gobbler test service started by :py:func:`~.start_gobbler`. If no
    test service was running, this function is a no-op.
    """
    global test_process 
    if test_process is not None:
        test_process.terminate()
        test_process = None
    return
