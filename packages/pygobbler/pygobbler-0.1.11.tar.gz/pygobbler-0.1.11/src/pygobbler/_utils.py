from typing import Optional, Dict, List
import json
import os
import tempfile
import requests


def format_error(res):
    ctype = res.headers["content-type"]
    if ctype == "application/json":
        info = res.json()
        return requests.HTTPError(res.status_code, info["reason"])
    elif ctype == "text/plain":
        return requests.HTTPError(res.status_code, res.text)
    else:
        return requests.HTTPError(res.status_code)


def dump_request(staging: str, url: str, action: str, payload: Dict, spoof: Optional[str] = None) -> str:
    if spoof is not None:
        payload = { **payload, "spoof": spoof }
    as_str = json.dumps(payload, indent=4)

    # Doing this little shuffle to get the right permissions. tempfile loves to
    # create 0o600 directories that the gobbler service account can't actually
    # read, so we just delete it and create it again under the more permissive
    # umask. Unfortunately we can't use chmod as this screws up FACLs.
    prefix = "request-" + action + "-"
    fd, holding_name = tempfile.mkstemp(dir=staging, prefix=prefix)
    os.close(fd)
    os.remove(holding_name)

    purge_holding = False
    try:
        with open(holding_name, "w") as handle:
            handle.write(as_str)
        purge_holding = True

        res = requests.post(url + "/new/" + os.path.basename(holding_name))
        if res.status_code >= 300:
            raise format_error(res)
        return res.json()

    finally:
        if purge_holding:
            os.remove(holding_name)
