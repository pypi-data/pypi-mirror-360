import pygobbler as pyg
import pytest
import os


@pytest.fixture(scope="module")
def setup():
    _, staging, registry, url = pyg.start_gobbler()
    pyg.remove_project("test", staging=staging, url=url)
    pyg.create_project("test", staging=staging, url=url)

    src = pyg.allocate_upload_directory(staging)
    with open(os.path.join(src, "foo"), "w") as handle:
        handle.write("BAR")
    pyg.upload_directory("test", "probation", "good", src, staging=staging, url=url, probation=True)
    pyg.upload_directory("test", "probation", "bad", src, staging=staging, url=url, probation=True)


def test_approve_probation(setup):
    _, staging, registry, url = pyg.start_gobbler()
    assert pyg.fetch_summary("test", "probation", "good", registry=registry, url=url)["on_probation"]
    assert pyg.fetch_latest("test", "probation", registry=registry, url=url) is None

    pyg.approve_probation("test", "probation", "good", staging=staging, url=url)
    assert "on_probation" not in pyg.fetch_summary("test", "probation", "good", registry=registry, url=url)
    assert pyg.fetch_latest("test", "probation", registry=registry, url=url) == "good"


def test_reject_probation(setup):
    _, staging, registry, url = pyg.start_gobbler()
    assert pyg.fetch_summary("test", "probation", "bad", registry=registry, url=url)["on_probation"]

    pyg.reject_probation("test", "probation", "bad", staging=staging, url=url)
    assert "bad" not in pyg.list_versions("test", "probation", registry=registry, url=url)
