import pytest
from typer.testing import CliRunner
from chinmoysay.main import app

runner = CliRunner()


def test_greet():
    result = runner.invoke(app, ["greet", "John"])
    assert result.exit_code == 0
    assert "Hi John" in result.stdout


def test_goodbye():
    result = runner.invoke(app, ["goodbye", "John"])
    assert result.exit_code == 0
    assert "Bye John" in result.stdout


def test_version():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "chinmoysay version 1.0.0" in result.stdout


def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "A friendly CLI app for greetings!" in result.stdout
