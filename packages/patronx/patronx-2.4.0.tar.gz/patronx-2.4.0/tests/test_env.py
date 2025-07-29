import os

import click
import pytest
from click.testing import CliRunner

from patronx.env import env_file_option, load_env_file


def test_load_env_file(tmp_path, monkeypatch):
    env_file = tmp_path / "vars"
    env_file.write_text("FOO=BAR\n")
    monkeypatch.delenv("FOO", raising=False)
    load_env_file(env_file)
    assert os.getenv("FOO") == "BAR"


def test_load_env_file_missing(tmp_path):
    missing = tmp_path / "none"
    with pytest.raises(click.ClickException):
        load_env_file(missing)


@click.command()
@env_file_option
def _cmd() -> None:
    click.echo(os.getenv("HELLO", ""))


def test_env_file_option(tmp_path, monkeypatch):
    env_file = tmp_path / "env"
    env_file.write_text("HELLO=WORLD\n")
    monkeypatch.delenv("HELLO", raising=False)
    runner = CliRunner()
    result = runner.invoke(_cmd, ["--env-file", str(env_file)])
    assert result.exit_code == 0
    assert "WORLD" in result.output