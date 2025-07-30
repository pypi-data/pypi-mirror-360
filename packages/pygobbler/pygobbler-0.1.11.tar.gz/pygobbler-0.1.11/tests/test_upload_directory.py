import pygobbler as pyg
import tempfile
import os
import pytest


@pytest.fixture(scope="module")
def setup():
    _, staging, registry, url = pyg.start_gobbler()

    pyg.remove_project("test-upload", staging=staging, url=url)
    pyg.remove_project("test-more-upload", staging=staging, url=url)
    pyg.remove_project("test-upload-perms", staging=staging, url=url)
    pyg.create_project("test-upload", staging=staging, url=url)
    pyg.create_project("test-more-upload", staging=staging, url=url)
    pyg.create_project("test-upload-perms", staging=staging, url=url)

    tmp = tempfile.mkdtemp()
    with open(os.path.join(tmp, "blah.txt"), "w") as f:
        f.write("BAR")
    os.mkdir(os.path.join(tmp, "foo"))
    with open(os.path.join(tmp, "foo", "bar.txt"), "w") as f:
        f.write("1 2 3 4 5 6 7 8 9 10")

    pyg.upload_directory(
        project="test-upload", 
        asset="jennifer", 
        version="1", 
        directory=tmp,
        staging=staging, 
        url=url
    )

    return tmp


def test_upload_directory_simple(setup):
    _, staging, registry, url = pyg.start_gobbler()

    # Checking that the files were, in fact, correctly uploaded.
    man = pyg.fetch_manifest("test-upload", "jennifer", "1", registry=registry, url=url)
    assert sorted(man.keys()) == ["blah.txt", "foo/bar.txt"]
    for k, v in man.items():
        assert "link" not in v

    # Deduplication happens naturally.
    pyg.upload_directory(
        project="test-upload", 
        asset="jennifer", 
        version="2", 
        directory=setup, # i.e., the 'tmp' returned by the setup.
        staging=staging,
        url=url
    )

    man = pyg.fetch_manifest("test-upload", "jennifer", "2", registry=registry, url=url)
    assert sorted(man.keys()) == ["blah.txt", "foo/bar.txt"]
    for k, v in man.items():
        assert "link" in v


def test_upload_directory_parallel(setup):
    _, staging, registry, url = pyg.start_gobbler()

    tmp = tempfile.mkdtemp()
    with open(os.path.join(tmp, "whee.txt"), "w") as handle:
        handle.write("motto motto")
    os.mkdir(os.path.join(tmp, "foo"))
    with open(os.path.join(tmp, "foo", "bar"), "w") as handle:
        handle.write("toki o kizuma uta")

    pyg.upload_directory(
        project="test-upload", 
        asset="penelope", 
        version="1", 
        directory=tmp,
        staging=staging, 
        url=url,
        concurrent=2
    )

    man = pyg.fetch_manifest("test-upload", "penelope", "1", registry=registry, url=url)
    assert sorted(man.keys()) == ["foo/bar", "whee.txt"]
    for k, v in man.items():
       assert not "link" in v


def test_upload_directory_empty_dirs(setup):
    _, staging, registry, url = pyg.start_gobbler()

    tmp = tempfile.mkdtemp()
    with open(os.path.join(tmp, "blah.txt"), "w") as handle:
        handle.write("motto motto")
    os.mkdir(os.path.join(tmp, "foo"))

    pyg.upload_directory(
        project="test-upload", 
        asset="violet", 
        version="1", 
        directory=tmp,
        staging=staging, 
        url=url
    )

    man = pyg.fetch_manifest("test-upload", "violet", "1", registry=registry, url=url)
    assert sorted(man.keys()) == ["blah.txt", "foo"]
    assert man["foo"]["md5sum"] == ""
    for k, v in man.items():
        assert "link" not in v


def test_upload_directory_links(setup):
    _, staging, registry, url = pyg.start_gobbler()

    dest = tempfile.mkdtemp()
    pyg.clone_version("test-upload", "jennifer", "2", dest, registry=registry)
    with open(os.path.join(dest, "whee"), "w") as f:
        f.write("BLAH")

    pyg.upload_directory(
        project="test-more-upload", 
        asset="natalie", 
        version="1", 
        directory=dest,
        staging=staging,
        url=url
    )

    man = pyg.fetch_manifest("test-more-upload", "natalie", "1", registry=registry, url=url)
    assert sorted(man.keys()) == ["blah.txt", "foo/bar.txt", "whee"]
    assert "link" in man["blah.txt"]
    assert "link" in man["foo/bar.txt"]
    assert "link" not in man["whee"]


def test_upload_directory_relative_links(setup):
    _, staging, registry, url = pyg.start_gobbler()

    dest = tempfile.mkdtemp()
    with open(os.path.join(dest, "blah.txt"), "w") as handle:
        handle.write("motto motto")
    os.symlink("blah.txt", os.path.join(dest, "whee.txt")) # relative links inside the directory are retained.
    os.mkdir(os.path.join(dest, "foo"))
    os.symlink("../whee.txt", os.path.join(dest, "foo/bar.txt")) 

    pyg.upload_directory(
        project="test-more-upload", 
        asset="nicole", 
        version="1", 
        directory=dest,
        staging=staging,
        url=url
    )

    man = pyg.fetch_manifest("test-more-upload", "nicole", "1", registry=registry, url=url)
    assert sorted(man.keys()) == [ "blah.txt", "foo/bar.txt", "whee.txt" ]
    assert "link" in man["whee.txt"]
    assert "link" in man["foo/bar.txt"]
    assert "link" not in man["blah.txt"]
    assert man["whee.txt"]["size"] == man["foo/bar.txt"]["size"]
    assert man["whee.txt"]["size"] == man["blah.txt"]["size"]


def test_upload_directory_staging(setup):
    _, staging, registry, url = pyg.start_gobbler()

    dir = pyg.allocate_upload_directory(staging)
    with open(os.path.join(dir, "blah.txt"), "w") as f:
        f.write("A B C D E")
    os.mkdir(os.path.join(dir, "foo"))
    with open(os.path.join(dir, "foo", "bar.txt"), "w") as f:
        f.write("1 2 3 4 5 6 7 8 9 10")

    pyg.upload_directory(
        project="test-upload", 
        asset="jennifer", 
        version="3", 
        directory=dir,
        staging=staging,
        url=url
    )

    man  = pyg.fetch_manifest("test-upload", "jennifer", "3", registry=registry, url=url)
    assert sorted(man.keys()) == ["blah.txt", "foo/bar.txt"]
    assert "link" not in man["blah.txt"]
    assert "link" in man["foo/bar.txt"]


def test_upload_directory_consume(setup):
    _, staging, registry, url = pyg.start_gobbler()

    dir = pyg.allocate_upload_directory(staging)
    with open(os.path.join(dir, "blah.txt"), "w") as f:
        f.write("A B C D E")
    os.mkdir(os.path.join(dir, "foo"))
    with open(os.path.join(dir, "foo", "bar.txt"), "w") as f:
        f.write("1 2 3 4 5 6 7 8 9 10")

    pyg.upload_directory(
        project="test-upload", 
        asset="anastasia", 
        version="1", 
        directory=dir,
        staging=staging,
        url=url,
        consume=False
    )
    assert os.path.exists(os.path.join(dir, "blah.txt"))
    assert os.path.exists(os.path.join(dir, "foo/bar.txt"))

    pyg.upload_directory(
        project="test-upload", 
        asset="victoria", 
        version="1", 
        directory=dir,
        staging=staging,
        url=url,
        consume=True
    )
    assert not os.path.exists(os.path.join(dir, "blah.txt"))
    assert not os.path.exists(os.path.join(dir, "foo/bar.txt"))


def test_upload_directory_ignore_dot(setup):
    _, staging, registry, url = pyg.start_gobbler()

    dir = pyg.allocate_upload_directory(staging)
    with open(os.path.join(dir, ".blah.txt"), "w") as f:
        f.write("A B C D E")
    os.mkdir(os.path.join(dir, ".foo"))
    with open(os.path.join(dir, ".foo", "bar.txt"), "w") as f:
        f.write("1 2 3 4 5 6 7 8 9 10")

    pyg.upload_directory(
        project="test-upload", 
        asset="annabelle", 
        version="0", 
        directory=dir,
        staging=staging,
        url=url
    )
    man = pyg.fetch_manifest("test-upload", "annabelle", "0", registry=registry, url=url)
    assert len(man) == 0

    pyg.upload_directory(
        project="test-upload", 
        asset="annabelle", 
        version="1", 
        directory=dir,
        staging=staging,
        url=url,
        ignore_dot=False
    )
    man = pyg.fetch_manifest("test-upload", "annabelle", "1", registry=registry, url=url)
    assert ".blah.txt" in man
    assert ".foo/bar.txt" in man


def test_allocate_upload_directory():
    _, staging, registry, url = pyg.start_gobbler()
    assert os.path.exists(pyg.allocate_upload_directory(staging))
    assert not os.path.exists(pyg.allocate_upload_directory(staging, create=False))
