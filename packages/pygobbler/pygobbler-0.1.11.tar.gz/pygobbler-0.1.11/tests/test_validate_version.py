import pygobbler as pyg
import tempfile
import os
import time
import pytest


def test_validate_version():
    _, staging, registry, url = pyg.start_gobbler()

    pyg.remove_project("test-validate", staging=staging, url=url)
    pyg.create_project("test-validate", staging=staging, url=url)

    src = pyg.allocate_upload_directory(staging)
    with open(os.path.join(src, "foo"), "w") as handle:
        handle.write("BAR")
    pyg.upload_directory("test-validate", "simple", "v1", src, staging=staging, url=url)
    pyg.validate_version("test-validate", "simple", "v1", staging=staging, url=url)

    # Adding another file directly to the registry.
    with open(os.path.join(registry, "test-validate", "simple", "v1", "whee"), "w") as handle:
        handle.write("stuff")
    with pytest.raises(Exception) as e:
        pyg.validate_version("test-validate", "simple", "v1", staging=staging, url=url)
    assert "extra file" in str(e) 
