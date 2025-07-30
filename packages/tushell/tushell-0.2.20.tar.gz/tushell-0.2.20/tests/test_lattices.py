import pytest
from click.testing import CliRunner
from tushell.lattices.curating_red_stones import execute_curating_red_stones
from tushell.lattices.echonode_trace_activation import execute_echonode_trace_activation
from tushell.lattices.enriched_version_fractale_001 import execute_enriched_version_fractale_001
from tushell.tushellcli import cli

def test_execute_curating_red_stones():
    result = execute_curating_red_stones()
    assert "Curating Red Stones Lattice Activated" in result

def test_execute_echonode_trace_activation():
    result = execute_echonode_trace_activation()
    assert "EchoNode Trace Activation Lattice Activated" in result

def test_execute_enriched_version_fractale_001():
    result = execute_enriched_version_fractale_001()
    assert "Enriched Version Fractale 001 Lattice Activated" in result

def test_cli_curating_red_stones():
    runner = CliRunner()
    result = runner.invoke(cli, ['curating-red-stones'])
    assert result.exit_code == 0
    assert "Curating Red Stones Lattice Activated" in result.output

def test_cli_activate_echonode_trace():
    runner = CliRunner()
    result = runner.invoke(cli, ['activate-echonode-trace'])
    assert result.exit_code == 0
    assert "EchoNode Trace Activation Lattice Activated" in result.output

def test_cli_enrich_fractale_version():
    runner = CliRunner()
    result = runner.invoke(cli, ['enrich-fractale-version'])
    assert result.exit_code == 0
    assert "Enriched Version Fractale 001 Lattice Activated" in result.output
