import pygobbler as pyg
import os


def _sort_array_of_actions(x):
    paths = [y["path"] for y in x]
    paths.sort()
    order = {}
    for i, p in enumerate(paths):
        order[p] = i
    output = [None] * len(x)
    for y in x:
        output[order[y["path"]]] = y
    return output


def test_reroute_links():
    _, staging, registry, url = pyg.start_gobbler()

    pyg.remove_project("test-reroute", staging=staging, url=url)
    pyg.create_project("test-reroute", staging=staging, url=url)

    src = pyg.allocate_upload_directory(staging)
    with open(os.path.join(src, "foo"), "w") as handle:
        handle.write("BAR")

    pyg.upload_directory("test-reroute", "simple", "v1", src, staging=staging, url=url)
    pyg.upload_directory("test-reroute", "simple", "v2", src, staging=staging, url=url)
    pyg.upload_directory("test-reroute", "simple", "v3", src, staging=staging, url=url)

    actions = pyg.reroute_links([{"project":"test-reroute", "asset":"simple", "version":"v1"}], staging=staging, url=url, dry_run=True)
    assert all([x["source"] == "test-reroute/simple/v1/foo" for x in actions])
    all_paths = [x["path"] for x in actions]
    assert "test-reroute/simple/v2/foo" in all_paths
    assert "test-reroute/simple/v3/foo" in all_paths
    all_copy = [x["copy"] for x in actions]
    assert all_copy[all_paths.index("test-reroute/simple/v2/foo")]
    assert not all_copy[all_paths.index("test-reroute/simple/v3/foo")]
    assert os.path.islink(os.path.join(registry, "test-reroute/simple/v2/foo")) 

    actions2 = pyg.reroute_links([{"project":"test-reroute", "asset":"simple", "version":"v1"}], staging=staging, url=url)
    assert _sort_array_of_actions(actions) == _sort_array_of_actions(actions2)
    assert not os.path.islink(os.path.join(registry, "test-reroute/simple/v2/foo")) 
