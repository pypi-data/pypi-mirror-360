# pygrid: Python client for the GRID esports API

[![Latest Version](https://img.shields.io/pypi/v/grid-lol-client?label=latest)](https://pypi.org/project/grid-lol-client/)
[![Python Versions](https://img.shields.io/pypi/pyversions/grid-lol-client)](https://pypi.org/project/grid-lol-client/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](/LICENSE)

pygrid simplifies the usage of the GRID esports API by managing all of the hard parts for you. A collection of data pipeline functions that support processing of game data are also provided with this library.

## Features & Todo
- [x] Rate limited access to GRID GraphQL endpoints.
- [x] Simple client class to access commonly used queries.
- [x] Automatic pagination for queries that require multiple API calls.
- [x] Minimal external dependencies. The client and ETL functions only require httpx, pendulum, pydantic, orjson and tqdm.
- [x] [Release on PyPi](https://pypi.org/project/grid-lol-client/) for easier installation.
- [x] Release my scripts that parse returned data files ideally in a database agnositic format. As I don't expect this library to become that popular, my main focus will be on compatability with my own [ATG](https://github.com/Allan-Cao/ATG) database format.
- [ ] Complete unit testing coverage of all parsing functions.
- [ ] Better documentation and figure out how to pass filtering options through the pagination function.

## Installation

```bash
pip install grid-lol-client
```

## Usage

```python
import os
from pygrid.client import GridClient

client = GridClient(os.environ["GRID_API_KEY"])
```

With the client setup with your GRID API key, you can now begin to request data from the centra data API.

```python
all_teams = client.get_all_teams()
3%|███▊                                          | 100/3629 [00:01<00:53, 65.66it/s]
```

Functions which call REST APIs will return an `httpx.response` object. Example usage:
```python
available_files = client.get_available_files("2796434")
next(file for file in available_files.json()["files"] if file["id"] == "events-grid")
{'id': 'events-grid',
 'description': 'Grid Series Events (.jsonl)',
 'status': 'ready',
 'fileName': 'events_2796434_grid.jsonl.zip',
 'fullURL': 'https://api.grid.gg/file-download/events/grid/series/2796434'}
```

Query for series with filters
```python
from pygrid import OrderDirection, SeriesType
import pendulum
available_series = client.get_all_series(
    order=OrderDirection.DESC,
    title_ids = [3], # Only LoL series (Val series by default also selected)
    gte = pendulum.now().add(weeks=-2).to_iso8601_string(), # Earliest series time
    game_types = [SeriesType.SCRIM], # COMPETITIVE is Champion's Queue
    # tournaments = ["825437", "825439", "825438", "825440", "825441"],
)
```
## Development

### Generating API clients with Ariadne Codegen
Ariadne Codegen lets us translate raw GraphQL queries into a Python library as well as bringing GraphQL's type safety to Python with Pydantic

You'll need to set your GRID API key to be able to access the central data GraphQL API
```bash
export GRID_API_KEY=YOUR_KEY_HERE
```

```bash
ariadne-codegen client --config central-data.toml
ariadne-codegen client --config series-state.toml
```

### Publishing and packaging

Poetry is used to manage packages and publishing to PyPi.
```bash
poetry add package_name -D # Development packages
poetry publish
```

## License

[MIT](https://choosealicense.com/licenses/mit/)
