import pygobbler as pyg


def test_set_permissions():
    _, staging, registry, url = pyg.start_gobbler()
    pyg.remove_project("test-perms", staging=staging, url=url)
    pyg.create_project("test-perms", staging=staging, url=url, owners=["LTLA"])

    until = "2022-02-02T02:20:02.02Z"
    pyg.set_permissions("test-perms",
        owners=["jkanche"], 
        uploaders=[ { "id": "lawremi", "until": until } ],
        staging=staging,
        url=url,
        registry=registry
    )

    perms = pyg.fetch_permissions("test-perms", registry=registry, url=url)
    assert perms["owners"] == [ "LTLA", "jkanche" ]
    assert len(perms["uploaders"]) == 1
    assert perms["uploaders"][0]["id"] == "lawremi"
    assert perms["uploaders"][0]["until"] == until
    assert not "global_write" in perms

    # Checking uploader appending, while also checking owners=NULL.
    pyg.set_permissions("test-perms", uploaders=[ { "id": "ArtifactDB-bot", "trusted": True } ], staging=staging, url=url, registry=registry)
    perms = pyg.fetch_permissions("test-perms", registry=registry, url=url)
    assert perms["owners"] == [ "LTLA", "jkanche" ]
    assert len(perms["uploaders"]) == 2
    assert perms["uploaders"][0]["id"] == "lawremi"
    assert perms["uploaders"][1]["id"] == "ArtifactDB-bot"
    assert perms["uploaders"][1]["trusted"]
    assert not "global_write" in perms

    # Checking union of owners, and also that uploaders=NULL works.
    pyg.set_permissions("test-perms", owners=[ "PeteHaitch", "LTLA" ], staging=staging, url=url, registry=registry)
    perms = pyg.fetch_permissions("test-perms", registry=registry, url=url)
    assert perms["owners"] == [ "LTLA", "jkanche", "PeteHaitch" ]
    assert len(perms["uploaders"]) == 2

    # Resetting the owners back.
    pyg.set_permissions("test-perms", owners=[ "LTLA" ], append=False, staging=staging, url=url, registry=registry)
    perms = pyg.fetch_permissions("test-perms", registry=registry, url=url)
    assert perms["owners"] == [ "LTLA" ]
    assert len(perms["uploaders"]) == 2

    # Dry run has no effect.
    new_perms = pyg.set_permissions("test-perms", owners=[ "foobar" ], uploaders= [], append=False, staging=staging, url=url, registry=registry, dry_run=True)
    assert new_perms["owners"] == [ "foobar" ]
    assert len(new_perms["uploaders"]) == 0
    perms = pyg.fetch_permissions("test-perms", registry=registry, url=url)
    assert perms["owners"] == [ "LTLA" ]
    assert len(perms["uploaders"]) == 2

    # Now resetting the uploaders. 
    pyg.set_permissions("test-perms", uploaders=[], append=False, staging=staging, url=url, registry=registry)
    perms = pyg.fetch_permissions("test-perms", registry=registry, url=url)
    assert perms["owners"] == [ "LTLA" ]
    assert len(perms["uploaders"]) == 0

    # Checking that it works with global writes enabled.
    pyg.set_permissions("test-perms", global_write=True, staging=staging, url=url, registry=registry)
    perms = pyg.fetch_permissions("test-perms", registry=registry, url=url)
    assert perms["global_write"] 


def test_set_asset_permissions():
    _, staging, registry, url = pyg.start_gobbler()
    pyg.remove_project("test-perms", staging=staging, url=url)
    pyg.create_project("test-perms", staging=staging, url=url, owners=["LTLA"])

    until = "2022-02-02T02:20:02.02Z"
    pyg.set_permissions("test-perms",
        asset="foobar",
        owners=["jkanche"], 
        uploaders=[ { "id": "lawremi", "until": until } ],
        staging=staging,
        url=url,
        registry=registry
    )

    perms = pyg.fetch_permissions("test-perms", asset="foobar", registry=registry, url=url)
    assert perms["owners"] == ["jkanche"]
    assert len(perms["uploaders"]) == 1
    assert perms["uploaders"][0]["id"] == "lawremi"
    assert perms["uploaders"][0]["until"] == until
    assert "global_write" not in perms

    # Works with remote.
    rperms = pyg.fetch_permissions("test-perms", asset="foobar", force_remote=True, registry=registry, url=url)
    assert rperms == perms

    # Works correctly when there are no permissions.
    perms = pyg.fetch_permissions("test-perms", asset="stuff", registry=registry, url=url)
    assert len(perms["owners"]) == 0
    assert len(perms["uploaders"]) == 0

    rperms = pyg.fetch_permissions("test-perms", asset="stuff", registry=registry, url=url)
    assert rperms == perms
