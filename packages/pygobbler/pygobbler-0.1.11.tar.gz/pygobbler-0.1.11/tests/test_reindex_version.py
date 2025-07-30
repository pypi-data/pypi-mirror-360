import pygobbler as pyg
import tempfile
import os
import time
import pytest


def test_reindex_version():
    _, staging, registry, url = pyg.start_gobbler()

    pyg.remove_project("test-reindex", staging=staging, url=url)
    pyg.create_project("test-reindex", staging=staging, url=url)

    src = pyg.allocate_upload_directory(staging)
    with open(os.path.join(src, "foo"), "w") as handle:
        handle.write("BAR")
    pyg.upload_directory("test-reindex", "simple", "v1", src, staging=staging, url=url)

    # Adding another file directly to the registry.
    with open(os.path.join(registry, "test-reindex", "simple", "v1", "whee"), "w") as handle:
        handle.write("stuff")

    # This does not show up in the manifest...
    man = pyg.fetch_manifest("test-reindex", "simple", "v1", registry=registry, url=url)
    assert list(man.keys()) == ["foo"]

    # until we reindex the version.
    pyg.reindex_version("test-reindex", "simple", "v1", staging=staging, url=url)
    man = pyg.fetch_manifest("test-reindex", "simple", "v1", registry=registry, url=url)
    assert sorted(list(man.keys())) == ["foo", "whee"]
