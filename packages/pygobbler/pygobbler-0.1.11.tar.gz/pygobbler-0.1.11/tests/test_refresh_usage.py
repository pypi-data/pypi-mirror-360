import pygobbler as pyg
import pytest
import os
import tempfile


@pytest.fixture(scope="module")
def setup():
    _, staging, registry, url = pyg.start_gobbler()

    pyg.remove_project("test-usage", staging=staging, url=url)
    pyg.create_project("test-usage", staging=staging, url=url)

    tmp = tempfile.mkdtemp()
    with open(os.path.join(tmp, "blah.txt"), "w") as f:
        f.write("BAR")
    os.mkdir(os.path.join(tmp, "foo"))
    with open(os.path.join(tmp, "foo", "bar.txt"), "w") as f:
        f.write("1 2 3 4 5 6 7 8 9 10")

    pyg.upload_directory(project="test-usage", asset="quota", version="v1", directory=tmp, staging=staging, url=url)


def test_refresh_usage(setup):
    _, staging, registry, url = pyg.start_gobbler()

    assert pyg.fetch_usage("test-usage", registry=registry, url=url) > 0

    with open(os.path.join(registry, "test-usage", "..usage"), "w") as handle:
        handle.write('{ "total": 0 }')
    assert pyg.fetch_usage("test-usage", registry=registry, url=url) == 0

    # Fixing the project usage.
    out = pyg.refresh_usage("test-usage", staging=staging, url=url)
    assert out > 0
    assert pyg.fetch_usage("test-usage", registry=registry, url=url) == out
