import pygobbler as pyg


def test_service_info():
    _, staging, registry, url = pyg.start_gobbler()
    payload = pyg.service_info(url)
    assert payload["staging"] == staging
    assert payload["registry"] == registry
