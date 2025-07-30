"""CLI 主命令测试"""

import pytest
from click.testing import CliRunner
from lhcli.cli import cli


def test_version():
    """测试版本显示"""
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "1.0.0" in result.output


def test_help():
    """测试帮助信息"""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "LightHope CLI Tools" in result.output


def test_diagram_mermaid_help():
    """测试 diagram mermaid 帮助"""
    runner = CliRunner()
    result = runner.invoke(cli, ["diagram", "mermaid", "--help"])
    assert result.exit_code == 0
    assert "Mermaid" in result.output
