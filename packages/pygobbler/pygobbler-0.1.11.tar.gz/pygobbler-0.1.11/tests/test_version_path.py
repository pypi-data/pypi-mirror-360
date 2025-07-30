import pygobbler as pyg
import tempfile
import os
import pytest


@pytest.fixture(scope="module")
def setup():
    _, staging, registry, url = pyg.start_gobbler()
    pyg.remove_project("test", staging=staging, url=url)
    pyg.create_project("test", staging=staging, url=url)

    tmp = tempfile.mkdtemp()
    with open(os.path.join(tmp, "blah.txt"), "w") as f:
        f.write("BAR")
    os.mkdir(os.path.join(tmp, "foo"))
    with open(os.path.join(tmp, "foo", "bar.txt"), "w") as f:
        f.write("1 2 3 4 5 6 7 8 9 10")

    pyg.upload_directory(
        project="test", 
        asset="serenity", 
        version="firefly", 
        directory=tmp,
        staging=staging, 
        url=url
    )


def test_version_path(setup):
    _, staging, registry, url = pyg.start_gobbler()
    out = pyg.version_path("test", "serenity", "firefly", registry=registry, url=url)
    assert out == os.path.join(registry, "test", "serenity", "firefly")
    with open(os.path.join(out, "blah.txt"), "r") as handle:
        assert handle.read() == "BAR"

    cache = tempfile.mkdtemp()
    out = pyg.version_path("test", "serenity", "firefly", registry=registry, url=url, cache=cache, force_remote=True)
    assert out.startswith(cache)
    assert out.endswith("test/serenity/firefly")
    with open(os.path.join(out, "foo", "bar.txt"), "r") as handle:
        assert handle.read() == "1 2 3 4 5 6 7 8 9 10"
