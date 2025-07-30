import pygobbler as pyg
import os
import pytest


@pytest.fixture(scope="module")
def setup():
    _, staging, registry, url = pyg.start_gobbler()

    pyg.remove_project("test", staging=staging, url=url)
    pyg.remove_project("more-list-test", staging=staging, url=url)
    pyg.create_project("test", staging=staging, url=url)
    pyg.create_project("more-list-test", staging=staging, url=url)

    src = pyg.allocate_upload_directory(staging)
    with open(os.path.join(src, "foo"), "w") as f:
        f.write("BAR")
    os.mkdir(os.path.join(src, "whee"))
    with open(os.path.join(src, "whee", "blah"), "w") as f:
        f.write("stuff")
    with open(os.path.join(src, "whee2"), "w") as f:
        f.write("ABCDEFGHIJK")

    pyg.upload_directory("test", "list", "v1", src, staging=staging, url=url)
    pyg.upload_directory("test", "list", "v2", src, staging=staging, url=url)
    pyg.upload_directory("test", "more-list", "foo", src, staging=staging, url=url)
    pyg.upload_directory("more-list-test", "list", "bar", src, staging=staging, url=url)


def test_list_projects(setup):
    _, staging, registry, url = pyg.start_gobbler()

    projects = pyg.list_projects(registry=registry, url=url)
    assert "test" in projects
    assert "more-list-test" in projects

    rprojects = pyg.list_projects(registry=registry, url=url, force_remote=True)
    assert sorted(projects) == sorted(rprojects)


def test_list_assets(setup):
    _, staging, registry, url = pyg.start_gobbler()

    assets = pyg.list_assets("test", registry=registry, url=url)
    assert "list" in assets
    assert "more-list" in assets

    rassets = pyg.list_assets("test", registry=registry, url=url, force_remote=True)
    assert sorted(assets) == sorted(rassets)


def test_list_versions(setup):
    _, staging, registry, url = pyg.start_gobbler()

    versions = pyg.list_versions("test", "list", registry=registry, url=url)
    assert "v1" in versions
    assert "v2" in versions

    rversions = pyg.list_versions("test", "list", registry=registry, url=url, force_remote=True)
    assert sorted(versions) == sorted(rversions)


def test_list_files(setup):
    _, staging, registry, url = pyg.start_gobbler()

    files = sorted(pyg.list_files("test", "list", "v1", registry=registry, url=url))
    assert files == sorted(["..summary", "..manifest", "foo", "whee/blah", "whee2"])
    rfiles = sorted(pyg.list_files("test", "list", "v1", registry=registry, url=url, force_remote=True))
    assert files == rfiles

    files = sorted(pyg.list_files("test", "list", "v1", registry=registry, url=url, include_dotdot=False))
    assert files == sorted(["foo", "whee/blah", "whee2"])
    rfiles = sorted(pyg.list_files("test", "list", "v1", registry=registry, url=url, include_dotdot=False, force_remote=True))
    assert files == rfiles

    files = sorted(pyg.list_files("test", "list", "v1", registry=registry, url=url, prefix="whee"))
    assert files == sorted(["whee/blah", "whee2"])
    rfiles = sorted(pyg.list_files("test", "list", "v1", registry=registry, url=url, force_remote=True, prefix="whee"))
    assert files == rfiles

    files = sorted(pyg.list_files("test", "list", "v1", registry=registry, url=url, prefix="whee/"))
    assert files == sorted(["whee/blah"])
    rfiles = sorted(pyg.list_files("test", "list", "v1", registry=registry, url=url, force_remote=True, prefix="whee/"))
    assert files == rfiles


def test_list_files_empty(setup):
    _, staging, registry, url = pyg.start_gobbler()

    src = pyg.allocate_upload_directory(staging)
    with open(os.path.join(src, "foo"), "w") as f:
        f.write("BAR")
    os.mkdir(os.path.join(src, "whee"))
    with open(os.path.join(src, "whee", "blah"), "w") as f:
        f.write("stuff")
    with open(os.path.join(src, "whee2"), "w") as f:
        f.write("ABCDEFGHIJK")
    os.mkdir(os.path.join(src, "whee", "stuff"))
    os.makedirs(os.path.join(src, "argo", "naut"))

    pyg.upload_directory("test", "list-empty", "v1", src, staging=staging, url=url)

    files = sorted(pyg.list_files("test", "list-empty", "v1", registry=registry, url=url))
    assert files == sorted(["..summary", "..manifest", "argo/naut/", "foo", "whee/blah", "whee/stuff/", "whee2"])
    rfiles = sorted(pyg.list_files("test", "list-empty", "v1", registry=registry, url=url, force_remote=True))
    assert files == rfiles
