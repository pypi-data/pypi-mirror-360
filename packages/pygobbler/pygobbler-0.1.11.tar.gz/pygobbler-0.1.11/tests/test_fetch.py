import pygobbler as pyg
import tempfile
import os
import pytest


@pytest.fixture(scope="module")
def setup():
    _, staging, registry, url = pyg.start_gobbler()

    pyg.remove_project("test", staging=staging, url=url)
    pyg.create_project("test", staging=staging, url=url)

    src = pyg.allocate_upload_directory(staging)
    with open(os.path.join(src, "foo"), "w") as f:
        f.write("BAR")
    os.mkdir(os.path.join(src, "whee"))
    with open(os.path.join(src, "whee", "blah"), "w") as f:
        f.write("stuff")

    pyg.upload_directory("test", "fetch", "v1", src, staging=staging, url=url)
    pyg.upload_directory("test", "fetch", "v2", src, staging=staging, url=url)


def test_fetch_manifest(setup):
    _, staging, registry, url = pyg.start_gobbler()

    man = pyg.fetch_manifest("test", "fetch", "v1", registry=registry, url=url)
    assert man["foo"]["size"] == 3
    assert man["whee/blah"]["size"] == 5

    cache = tempfile.mkdtemp()
    rman = pyg.fetch_manifest("test", "fetch", "v1", registry=registry, url=url, cache=cache, force_remote=True)
    assert man == rman


def test_fetch_summary(setup):
    _, staging, registry, url = pyg.start_gobbler()

    summ = pyg.fetch_summary("test", "fetch", "v1", registry=registry, url=url)
    assert isinstance(summ["upload_user_id"], str)
    assert isinstance(summ["upload_start"], str)
    assert isinstance(summ["upload_finish"], str)

    cache = tempfile.mkdtemp()
    rsumm = pyg.fetch_summary("test", "fetch", "v1", registry=registry, url=url, cache=cache, force_remote=True)
    assert summ == rsumm


def test_fetch_latest(setup):
    _, staging, registry, url = pyg.start_gobbler()

    assert pyg.fetch_latest("test", "fetch", registry=registry, url=url) == "v2"
    assert pyg.fetch_latest("test", "missing", registry=registry, url=url) is None
    assert pyg.fetch_latest("test", "fetch", registry=registry, url=url, force_remote=True) == "v2"
    assert pyg.fetch_latest("test", "missing", registry=registry, url=url, force_remote=True) is None


def test_fetch_usage(setup):
    _, staging, registry, url = pyg.start_gobbler()

    assert pyg.fetch_usage("test", registry=registry, url=url) > 0
    assert pyg.fetch_usage("test", registry=registry, url=url, force_remote=True) > 0


def test_fetch_permissions(setup):
    _, staging, registry, url = pyg.start_gobbler()

    perms = pyg.fetch_permissions("test", registry=registry, url=url)
    assert isinstance(perms["owners"], list)
    assert isinstance(perms["uploaders"], list)

    rperms = pyg.fetch_permissions("test", registry=registry, url=url, force_remote=True)
    assert perms == rperms


def test_fetch_file(setup):
    _, staging, registry, url = pyg.start_gobbler()

    p = pyg.fetch_file("test/fetch/v1/foo", registry=registry, url=url)
    assert p.startswith(registry)
    with open(p, "r") as handle:
        assert handle.read() == "BAR"

    cache = tempfile.mkdtemp()
    p = pyg.fetch_file("test/fetch/v1/whee/blah", registry=registry, url=url, cache=cache, force_remote=True)
    assert p.startswith(cache)
    with open(p, "r") as handle:
        assert handle.read() == "stuff"


def test_fetch_directory(setup):
    _, staging, registry, url = pyg.start_gobbler()

    dir = pyg.fetch_directory("test/fetch/v2", registry=registry, url=url)
    assert dir.startswith(registry)
    with open(os.path.join(dir, "foo"), "r") as handle:
        assert handle.read() == "BAR"

    cache = tempfile.mkdtemp()
    rdir = pyg.fetch_directory("test/fetch/v2", registry=registry, url=url, cache=cache, force_remote=True)
    assert rdir.startswith(cache)
    with open(os.path.join(dir, "foo"), "r") as handle:
        assert handle.read() == "BAR"
    with open(os.path.join(dir, "whee", "blah"), "r") as handle:
        assert handle.read() == "stuff"

    # Subsequent requests are no-ops.
    with open(os.path.join(rdir, "foo"), "w") as handle:
        handle.write("more-bar")
    rdir2 = pyg.fetch_directory("test/fetch/v2", registry=registry, url=url, cache=cache, force_remote=True)
    assert rdir == rdir2
    with open(os.path.join(rdir2, "foo"), "r") as handle:
        assert handle.read() == "more-bar"

    # Unless we force an overwrite.
    rdir2 = pyg.fetch_directory("test/fetch/v2", registry=registry, url=url, cache=cache, force_remote=True, overwrite=True)
    with open(os.path.join(rdir2, "foo"), "r") as handle:
        assert handle.read() == "BAR"

    # Trying with multiple cores.
    cache = tempfile.mkdtemp()
    rdir2 = pyg.fetch_directory("test/fetch/v2", registry=registry, url=url, cache=cache, force_remote=True, concurrent=2)
    with open(os.path.join(rdir2, "foo"), "r") as handle:
        assert handle.read() == "BAR"


def test_fetch_directory(setup):
    _, staging, registry, url = pyg.start_gobbler()

    src = pyg.allocate_upload_directory(staging)
    with open(os.path.join(src, "foo"), "w") as f:
        f.write("BAR")
    os.mkdir(os.path.join(src, "whee"))
    with open(os.path.join(src, "whee", "blah"), "w") as f:
        f.write("stuff")
    os.mkdir(os.path.join(src, "whee", "stuff"))
    os.makedirs(os.path.join(src, "chihaya", "kisaragi"))

    pyg.upload_directory("test", "fetch-empty", "v1", src, staging=staging, url=url)

    cache = tempfile.mkdtemp()
    rdir2 = pyg.fetch_directory("test/fetch-empty/v1", registry=registry, url=url, cache=cache, force_remote=True, concurrent=2)

    with open(os.path.join(rdir2, "foo"), "r") as handle:
        assert handle.read() == "BAR"
    with open(os.path.join(rdir2, "whee", "blah"), "r") as handle:
        assert handle.read() == "stuff"

    assert os.path.isdir(os.path.join(rdir2, "whee", "stuff"))
    assert os.path.isdir(os.path.join(rdir2, "chihaya", "kisaragi"))
