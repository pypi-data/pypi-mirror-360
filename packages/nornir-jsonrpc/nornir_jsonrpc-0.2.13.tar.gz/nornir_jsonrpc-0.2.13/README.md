# Nornir JSON RPC Plugin

[![Build Status](https://github.com/dgethings/nornir_jsonrpc/workflows/CI/badge.svg)](https://github.com/dgethings/nornir_jsonrpc/actions)
[![PyPI version](https://badge.fury.io/py/nornir-jsonrpc.svg)](https://badge.fury.io/py/nornir-jsonrpc)
[![Python versions](https://img.shields.io/pypi/pyversions/nornir-jsonrpc.svg)](https://pypi.python.org/pypi/nornir-jsonrpc)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Fdgethings%2Fnornir_jsonrpc%2Frefs%2Fheads%2Fmain%2Fpyproject.toml)

Nornir plugin for JSON-RPC.

## Installation

```bash
pip install nornir-jsonrpc
```

```bash
uv add nornir-jsonrpc
```

## Plugins

### Connection

* `jsonrpc`: uses `httpx` to connect to a device and transport JSON-RPC.

### Tasks

* `jsonrpc_cli`: Execute a CLI command.
* `jsonrpc_get`: Retrieve data from the device.
* `jsonrpc_set`: Set data on the device.
* `jsonrpc_update_config`: Update a configuration element.
* `jsonrpc_replace_config`: Replace a configuration element.
* `jsonrpc_delete_config`: Delete a configuration element.

## Usage

```python
from nornir import InitNornir
from nornir_jsonrpc.tasks import jsonrpc_cli
from nornir_utils.plugins.functions import print_result

nr = InitNornir(config_file="config.yaml")

result = nr.run(
    task=jsonrpc_cli,
    cmds=["show version"],
)

print_result(result)
```

## License

[MIT](LICENSE)
