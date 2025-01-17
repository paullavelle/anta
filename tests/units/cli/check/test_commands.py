# Copyright (c) 2023 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the LICENSE file.
"""
Tests for anta.cli.check.commands
"""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from anta.cli import anta
from tests.lib.utils import default_anta_env

if TYPE_CHECKING:
    from click.testing import CliRunner
    from pytest import CaptureFixture

DATA_DIR: Path = Path(__file__).parents[3].resolve() / "data"


@pytest.mark.parametrize(
    "catalog_path, expected_exit, expected_output",
    [
        pytest.param("ghost_catalog.yml", 2, "Error: Invalid value for '--catalog'", id="catalog does not exist"),
        pytest.param("test_catalog_with_undefined_module.yml", 2, "Unable to load ANTA Test Catalog", id="catalog is not valid"),
        pytest.param("test_catalog.yml", 0, f"Catalog {DATA_DIR}/test_catalog.yml is valid", id="catalog valid"),
    ],
)
def test_catalog(capsys: CaptureFixture[str], click_runner: CliRunner, catalog_path: Path, expected_exit: int, expected_output: str) -> None:
    """
    Test `anta check catalog -c catalog
    """
    env = default_anta_env()
    catalog_full_path = DATA_DIR / catalog_path
    cli_args = ["check", "catalog", "-c", str(catalog_full_path)]
    with capsys.disabled():
        result = click_runner.invoke(anta, cli_args, env=env, auto_envvar_prefix="ANTA")
    assert result.exit_code == expected_exit
    assert expected_output in result.output
