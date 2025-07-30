import pygobbler as pyg


def test_unpack_path():
    out = pyg.unpack_path("project/asset/version/path")
    assert out["project"] == "project"
    assert out["asset"] == "asset"
    assert out["version"] == "version"
    assert out["path"] == "path"

    out = pyg.unpack_path("project/asset/version/foo/bar")
    assert out["project"] == "project"
    assert out["asset"] == "asset"
    assert out["version"] == "version"
    assert out["path"] == "foo/bar"

    out = pyg.unpack_path("project/asset/version/")
    assert out["project"] == "project"
    assert out["asset"] == "asset"
    assert out["version"] == "version"
    assert out["path"] is None

    out = pyg.unpack_path("project/asset/version")
    assert out["project"] == "project"
    assert out["asset"] == "asset"
    assert out["version"] == "version"
    assert out["path"] is None
