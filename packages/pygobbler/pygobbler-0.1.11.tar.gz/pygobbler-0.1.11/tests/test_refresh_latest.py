import pygobbler as pyg
import pytest
import os
import time
import tempfile


@pytest.fixture(scope="module")
def setup():
    _, staging, registry, url = pyg.start_gobbler()

    pyg.remove_project("test", staging=staging, url=url)
    pyg.create_project("test", staging=staging, url=url)

    tmp = tempfile.mkdtemp()
    pyg.upload_directory(project="test", asset="latest", version="v1", directory=tmp, staging=staging, url=url)
    time.sleep(1.1)
    pyg.upload_directory(project="test", asset="latest", version="v2", directory=tmp, staging=staging, url=url)
    time.sleep(1.1)
    pyg.upload_directory(project="test", asset="latest", version="v3", directory=tmp, staging=staging, url=url)


def test_refresh_latest(setup):
    _, staging, registry, url = pyg.start_gobbler()

    assert pyg.fetch_latest("test", "latest", registry=registry, url=url) == "v3"

    os.unlink(os.path.join(registry, "test", "latest", "..latest"))
    assert pyg.fetch_latest("test", "latest", registry=registry, url=url) is None 

    v = pyg.refresh_latest("test", "latest", staging=staging, url=url)
    assert v == "v3"
    assert pyg.fetch_latest("test", "latest", registry=registry, url=url) == "v3"
