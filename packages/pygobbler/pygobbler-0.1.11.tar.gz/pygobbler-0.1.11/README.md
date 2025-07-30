<!-- These are examples of badges you might want to add to your README:
     please update the URLs accordingly

[![Built Status](https://api.cirrus-ci.com/github/<USER>/pygobbler.svg?branch=main)](https://cirrus-ci.com/github/<USER>/pygobbler)
[![ReadTheDocs](https://readthedocs.org/projects/pygobbler/badge/?version=latest)](https://pygobbler.readthedocs.io/en/stable/)
[![Coveralls](https://img.shields.io/coveralls/github/<USER>/pygobbler/main.svg)](https://coveralls.io/r/<USER>/pygobbler)
[![Conda-Forge](https://img.shields.io/conda/vn/conda-forge/pygobbler.svg)](https://anaconda.org/conda-forge/pygobbler)
[![Monthly Downloads](https://pepy.tech/badge/pygobbler/month)](https://pepy.tech/project/pygobbler)
[![Twitter](https://img.shields.io/twitter/url/http/shields.io.svg?style=social&label=Twitter)](https://twitter.com/pygobbler)
-->

# Python client for the gobbler service

![Unit tests](https://github.com/ArtifactDB/gobbler-py/actions/workflows/run-tests.yaml/badge.svg)
![Documentation](https://github.com/ArtifactDB/gobbler-py/actions/workflows/build-docs.yaml/badge.svg)
[![PyPI-Server](https://img.shields.io/pypi/v/pygobbler.svg)](https://pypi.org/project/pygobbler/)

Pretty much as it says on the tin; provides an Python client for the [Gobbler service](https://github.com/ArtifactDB/gobbler).
It is assumed that the users of this package and the Gobbler service itself are accessing the same shared filesystem;
this is typically the case for high-performance computing (HPC) clusters in scientific institutions.
To demonstrate, let's spin up a mock Gobbler instance:

```python
import pygobbler as pyg
_, staging, registry, url = pyg.start_gobbler()
```

Administrators are responsible for creating projects:

```python
pyg.create_project("test", staging=staging, url=url, owners=["akari"])
```

An authorized user account (in this case, `akari`) can then upload directory of arbitrary files:

```python
import tempfile
import os
tmp = tempfile.mkdtemp()
with open(os.path.join(tmp, "blah.txt"), "w") as f:
    f.write("BAR")
os.mkdir(os.path.join(tmp, "foo"))
with open(os.path.join(tmp, "foo", "bar.txt"), "w") as f:
    f.write("1 2 3 4 5 6 7 8 9 10")

pyg.upload_directory(
    project="test", 
    asset="foo", 
    version="bar", 
    directory=tmp,
    staging=staging, 
    url=url
)
```

Anyone can fetch or list the contents, either on the same filesystem or remotely via the REST API.

```python
pyg.list_files("test", "foo", "bar", registry=registry, url=url)
pyg.fetch_manifest("test", "foo", "bar", registry=registry, url=url)
pyg.fetch_summary("test", "foo", "bar", registry=registry, url=url)
pyg.fetch_file("test/foo/bar/blah.txt", registry=registry, url=url)
pyg.version_path("test", "foo", "bar", registry=registry, url=url)
```

Project owners can set the permissions to allow other users to add new assets or new versions of existing assets:

```python
pyg.set_permissions(
    "test", 
    uploaders=[ { "id": "alicia", "asset": "foo" } ], 
    registry=registry, 
    staging=staging, 
    url=url
)

# And then 'alicia' can do:
pyg.upload_directory(
    project="test", 
    asset="foo", 
    version="bar2", 
    directory=tmp,
    staging=staging, 
    url=url
)
```

By default, `uploaders` are untrusted and their uploads will be "probational".
Owners can approve/reject probational uploads after review.

```python
pyg.approve_probation("test", "foo", "bar2", staging=staging, url=url)
```

Finally, administrators can delete projects, though this should be done sparingly.

```python
pyg.remove_project("test", staging=staging, url=url)
```

Check out the [API documentation](https://artifactdb.github.io/gobbler-py/) for more details on each function.
For the concepts underlying the Gobbler itself, check out the [repository](https://github.com/ArtifactDB/gobbler) for a detailed explanation.
