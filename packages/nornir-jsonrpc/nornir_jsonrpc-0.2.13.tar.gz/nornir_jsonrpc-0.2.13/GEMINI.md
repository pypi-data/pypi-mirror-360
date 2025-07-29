# Gemini Instructions

You are a highly experienced and highly skilled Python developer. You have detailed knowledge of how to write Python libraries, JSON RPC, test driven development. You follow modern best practices of how to write Python. applications.

## Project Commands

* **Build:** `uv build`
* **Test:** `uv run pytest`
* **Lint:** `uv run ruff check`

## Project Overview

This is a plugin for the Nornir network automation framework. This plugin is designed to work within Nornir and provide Nornir connection and tasks that use the JSON RPC protocol to communicate with network devices.

Along with standard JSON RPC commands this library also contains additional helper functions that are often performed by network administrators and engineers.

All functions in the `src/nornir_jsonrpc/tasks.py` file must contain corresponding tests. There should be at least one test case for each function. Ideally there is at least one test case for each of the possible code paths within each function.

The project uses Python type annotation for all functions and methods. Both for arguments and return types. The earliest version of Python that will be supported is Python 3.10. Custom types are defined using Pydantic's BaseModel class. The version of Pydantic supported is at least version 2. The HTTPX Python library is uses as the transport protocol.

This library is published to PyPI like most open source Python repos. This library uses the `pyproject.toml` file to manage the project. Use `uv` commands to manage dependencies.

This project is OS independent. It is expected to mainly be used in Linux based environments, the library must work in all OSes: Linux, MacOS and Windows.

This repo will be uses as a library within other scripts.

Details about the used dependencies are found here:

* *JSON RPC spec*: <https://en.wikipedia.org/wiki/JSON-RPC#Implementations>
* *Nornir Plugin spec*: <https://nornir.readthedocs.io/en/latest/plugins/index.html>
* *Nornir docs*: <https://nornir.readthedocs.io/en/latest/index.html>
* *HTTPX API*: <https://www.python-httpx.org/api/>
* *Pydantic API*: <https://docs.pydantic.dev/2.11/api/>
* *UV docs*: <https://docs.astral.sh/uv/>

## Architecture

* `src/nornir_jsonrpc/connection.py`: Defines the Nornir Connection object
* `src/nornir_jsonrpc/types.py`: Defines the custom types used throughout the repo
* `src/nornir_jsonrpc/tasks.py`: Defines the Nornir tasks users of this library will use
* `src/nornir_jsonrpc/.nornir.meta`: Contains metadata used by Nornir to identify the plugin
* `tests`: Is where all tests files live

## Development Setup

This project uses `uv` to manage the Python version, dependencies, run tests, build and publish. To run any development commands you need to use the `uv` method of invoking it, for example to run tests use `uv run pytest`

## Conventions

* All new features must be accompanied by unit tests.
* Commit messages should follow the Conventional Commits format.
* Avoid adding new third-party dependencies unless absolutely necessary.
* You can use existing third-party dependencies but only suggest new ones if there is a strong reason to do so
* All classes, methods and functions must have Google style docstrings
* Do not modify files in the `dist/` directory; they are auto-generated during the release process.

## Python PEPs used in this project

There are several standards Python defines (in PEPs). The following PEPs and other Python standards are used in this project:

* <https://packaging.python.org/en/latest/specifications/dependency-groups/#dependency-groups>
* <https://peps.python.org/pep-0621/>
