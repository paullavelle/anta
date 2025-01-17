<!--
  ~ Copyright (c) 2023 Arista Networks, Inc.
  ~ Use of this source code is governed by the Apache License 2.0
  ~ that can be found in the LICENSE file.
  -->

# How to contribute to ANTA

Contribution model is based on a fork-model. Don't push to arista-netdevops-community/anta directly. Always do a branch in your forked repository and create a PR.

To help development, open your PR as soon as possible even in draft mode. It helps other to know on what you are working on and avoid duplicate PRs.

## Create a development environement

Run the following commands to create an ANTA development environement:

```bash
# Clone repository
$ git clone https://github.com/arista-netdevops-community/anta.git
$ cd anta

# Install ANTA in editable mode and its development tools
$ pip install -e .[dev]

# Verify installation
$ pip list -e
Package Version Editable project location
------- ------- -------------------------
anta    0.11.0   /mnt/lab/projects/anta
```

Then, [`tox`](https://tox.wiki/) is configued with few environments to run CI locally:

```bash
$ tox list -d
default environments:
clean  -> Erase previous coverage reports
lint   -> Check the code style
type   -> Check typing
py38   -> Run pytest with py38
py39   -> Run pytest with py39
py310  -> Run pytest with py310
py311  -> Run pytest with py311
report -> Generate coverage report
```

### Code linting

```bash
tox -e lint
[...]
lint: commands[0]> black --check --diff --color .
All done! ✨ 🍰 ✨
104 files would be left unchanged.
lint: commands[1]> isort --check --diff --color .
Skipped 7 files
lint: commands[2]> flake8 --max-line-length=165 --config=/dev/null anta
lint: commands[3]> flake8 --max-line-length=165 --config=/dev/null tests
lint: commands[4]> pylint anta

--------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)

.pkg: _exit> python /Users/guillaumemulocher/.pyenv/versions/3.8.13/envs/anta/lib/python3.8/site-packages/pyproject_api/_backend.py True setuptools.build_meta
  lint: OK (19.26=setup[5.83]+cmd[1.50,0.76,1.19,1.20,8.77] seconds)
  congratulations :) (19.56 seconds)
```

### Code Typing

```bash
tox -e type

[...]
type: commands[0]> mypy --config-file=pyproject.toml anta
Success: no issues found in 52 source files
.pkg: _exit> python /Users/guillaumemulocher/.pyenv/versions/3.8.13/envs/anta/lib/python3.8/site-packages/pyproject_api/_backend.py True setuptools.build_meta
  type: OK (46.66=setup[24.20]+cmd[22.46] seconds)
  congratulations :) (47.01 seconds)
```

> NOTE: Typing is configured quite strictly, do not hesitate to reach out if you have any questions, struggles, nightmares.

## Unit tests

To keep high quality code, we require to provide a Pytest for every tests implemented in ANTA.

All submodule should have its own pytest section under `tests/units/anta_tests/<submodule-name>.py`.

### How to write a unit test for an AntaTest subclass

The Python modules in the `tests/units/anta_tests` folder  define test parameters for AntaTest subclasses unit tests.
A generic test function is written for all unit tests in `tests.lib.anta` module.
The `pytest_generate_tests` function definition in `conftest.py` is called during test collection.
The `pytest_generate_tests` function will parametrize the generic test function based on the `DATA` data structure defined in `tests.units.anta_tests` modules.
See https://docs.pytest.org/en/7.3.x/how-to/parametrize.html#basic-pytest-generate-tests-example

The `DATA` structure is a list of dictionaries used to parametrize the test.
The list elements have the following keys:
- `name` (str): Test name as displayed by Pytest.
- `test` (AntaTest): An AntaTest subclass imported in the test module - e.g. VerifyUptime.
- `eos_data` (list[dict]): List of data mocking EOS returned data to be passed to the test.
- `inputs` (dict): Dictionary to instantiate the `test` inputs as defined in the class from `test`.
- `expected` (dict): Expected test result structure, a dictionary containing a key
    `result` containing one of the allowed status (`Literal['success', 'failure', 'unset', 'skipped', 'error']`) and optionally a key `messages` which is a list(str) and each message is expected to  be a substring of one of the actual messages in the TestResult object.


In order for your unit tests to be correctly collected, you need to import the generic test function even if not used in the Python module.

Test example for `anta.tests.system.VerifyUptime` AntaTest.

``` python
# Import the generic test function
from tests.lib.anta import test  # noqa: F401

# Import your AntaTest
from anta.tests.system import VerifyUptime

# Define test parameters
DATA: list[dict[str, Any]] = [
   {
        # Arbitrary test name
        "name": "success",
        # Must be an AntaTest definition
        "test": VerifyUptime,
        # Data returned by EOS on which the AntaTest is tested
        "eos_data": [{"upTime": 1186689.15, "loadAvg": [0.13, 0.12, 0.09], "users": 1, "currentTime": 1683186659.139859}],
        # Dictionary to instantiate VerifyUptime.Input
        "inputs": {"minimum": 666},
        # Expected test result
        "expected": {"result": "success"},
    },
    {
        "name": "failure",
        "test": VerifyUptime,
        "eos_data": [{"upTime": 665.15, "loadAvg": [0.13, 0.12, 0.09], "users": 1, "currentTime": 1683186659.139859}],
        "inputs": {"minimum": 666},
        # If the test returns messages, it needs to be expected otherwise test will fail.
        # NB: expected messages only needs to be included in messages returned by the test. Exact match is not required.
        "expected": {"result": "failure", "messages": ["Device uptime is 665.15 seconds"]},
    },
]
```

## Git Pre-commit hook

```bash
pip install pre-commit
pre-commit install
```

When running a commit or a pre-commit check:

``` bash
❯ echo "import foobaz" > test.py && git add test.py
❯ pre-commit
pylint...................................................................Failed
- hook id: pylint
- exit code: 22

************* Module test
test.py:1:0: C0114: Missing module docstring (missing-module-docstring)
test.py:1:0: E0401: Unable to import 'foobaz' (import-error)
test.py:1:0: W0611: Unused import foobaz (unused-import)
```

> NOTE: It could happen that pre-commit and tox disagree on something, in that case please open an issue on Github so we can take a look.. It is most probably wrong configuration on our side.

## Configure MYPYPATH

In some cases, mypy can complain about not having `MYPYPATH` configured in your shell. It is especially the case when you update both an anta test and its unit test. So you can configure this environment variable with:

```bash
# Option 1: use local folder
export MYPYPATH=.

# Option 2: use absolute path
export MYPYPATH=/path/to/your/local/anta/repository
```

## Documentation

[`mkdocs`](https://www.mkdocs.org/) is used to generate the documentation. A PR should always update the documentation to avoid documentation debt.

### Install documentation requirements

Run pip to install the documentation requirements from the root of the repo:

```bash
pip install -e .[doc]
```

### Testing documentation

You can then check locally the documentation using the following command from the root of the repo:

```bash
mkdocs serve
```

By default, `mkdocs` listens to http://127.0.0.1:8000/, if you need to expose the documentation to another IP or port (for instance all IPs on port 8080), use the following command:

```bash
mkdocs serve --dev-addr=0.0.0.0:8080
```

### Build class diagram

To build class diagram to use in API documentation, you can use `pyreverse` part of `pylint` with [`graphviz`](https://graphviz.org/) installed for jpeg generation.

```bash
pyreverse anta --colorized -a1 -s1 -o jpeg -m true -k --output-directory docs/imgs/uml/ -c <FQDN anta class>
```

Image will be generated under `docs/imgs/uml/` and can be inserted in your documentation.

### Checking links

Writing documentation is crucial but managing links can be cumbersome. To be sure there is no dead links, you can use [`muffet`](https://github.com/raviqqe/muffet) with the following command:

```bash
muffet -c 2 --color=always http://127.0.0.1:8000 -e fonts.gstatic.com
```

## Continuous Integration

GitHub actions is used to test git pushes and pull requests. The workflows are defined in this [directory](https://github.com/arista-netdevops-community/anta/tree/main/.github/workflows). We can view the results [here](https://github.com/arista-netdevops-community/anta/actions).
