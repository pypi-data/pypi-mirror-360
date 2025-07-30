"""Tests for the echo-sync command."""

import os
import json
import pytest
from unittest.mock import Mock, patch
from click.testing import CliRunner
from tushell.tushellcli import echo_sync

@pytest.fixture
def runner():
    """Create a CLI runner for testing."""
    return CliRunner()

@pytest.fixture
def mock_client():
    """Create a mock EchoSyncClient."""
    client = Mock()
    client.push_state.return_value = {
        "status": "success",
        "message": "State pushed successfully",
        "conflicts": [],
        "metrics": {
            "duration_ms": 100,
            "data_size": 1024
        }
    }
    client.pull_state.return_value = {
        "node_id": "test-node",
        "data": {"key": "value"},
        "version": "1.0",
        "metrics": {
            "duration_ms": 100,
            "data_size": 1024
        }
    }
    client.get_node_status.return_value = {
        "node_id": "test-node",
        "is_online": True,
        "last_sync": "2024-04-16T12:00:00Z",
        "version": "1.0",
        "status": "active",
        "metrics": {
            "sync_count": 10,
            "error_rate": 0.0
        }
    }
    client.get_node_history.return_value = [
        {
            "timestamp": "2024-04-16T12:00:00Z",
            "operation": "push",
            "status": "success",
            "details": "State updated"
        }
    ]
    client.get_nodes.return_value = [
        {"id": "node-1", "status": "active"},
        {"id": "node-2", "status": "active"}
    ]
    return client

@pytest.fixture
def env_vars():
    """Set up environment variables for testing."""
    os.environ["ECHO_API_URL"] = "http://test-api"
    os.environ["ECHO_TOKEN"] = "test-token"
    yield
    del os.environ["ECHO_API_URL"]
    del os.environ["ECHO_TOKEN"]

def test_echo_sync_basic_pull(runner, mock_client, env_vars):
    """Test basic pull operation."""
    with patch("tushell.tushellcli.EchoSyncClient", return_value=mock_client):
        result = runner.invoke(echo_sync, ["--node-id", "test-node"])
        assert result.exit_code == 0
        assert "Data successfully pulled from remote nodes" in result.output

def test_echo_sync_basic_push(runner, mock_client, env_vars):
    """Test basic push operation."""
    with patch("tushell.tushellcli.EchoSyncClient", return_value=mock_client):
        result = runner.invoke(echo_sync, ["--node-id", "test-node", "--action", "push"])
        assert result.exit_code == 0
        assert "Data successfully pushed to remote nodes" in result.output

def test_echo_sync_with_conflicts(runner, mock_client, env_vars):
    """Test push operation with conflicts."""
    mock_client.push_state.return_value = {
        "status": "conflict",
        "conflicts": [{"field": "data", "local": "old", "remote": "new"}]
    }
    mock_client.resolve_conflicts.return_value = {
        "success": True,
        "message": "Conflicts resolved"
    }
    
    with patch("tushell.tushellcli.EchoSyncClient", return_value=mock_client):
        result = runner.invoke(echo_sync, [
            "--node-id", "test-node",
            "--action", "push",
            "--verbose"
        ])
        assert result.exit_code == 0
        assert "Conflicts detected" in result.output
        assert "Conflicts resolved successfully" in result.output

def test_echo_sync_status(runner, mock_client, env_vars):
    """Test status operation."""
    with patch("tushell.tushellcli.EchoSyncClient", return_value=mock_client):
        result = runner.invoke(echo_sync, [
            "--node-id", "test-node",
            "--action", "status",
            "--verbose"
        ])
        assert result.exit_code == 0
        assert "Node Status Report" in result.output
        assert "Online: ✅" in result.output

def test_echo_sync_history(runner, mock_client, env_vars):
    """Test history operation."""
    with patch("tushell.tushellcli.EchoSyncClient", return_value=mock_client):
        result = runner.invoke(echo_sync, [
            "--node-id", "test-node",
            "--action", "history",
            "--verbose"
        ])
        assert result.exit_code == 0
        assert "Node History" in result.output
        assert "Operation: push" in result.output

def test_echo_sync_batch(runner, mock_client, env_vars):
    """Test batch operation."""
    with patch("tushell.tushellcli.EchoSyncClient", return_value=mock_client):
        result = runner.invoke(echo_sync, [
            "--node-id", "test-node",
            "--action", "batch",
            "--batch-size", "2",
            "--verbose"
        ])
        assert result.exit_code == 0
        assert "Processed 2 of 2 nodes" in result.output

def test_echo_sync_with_metrics(runner, mock_client, env_vars):
    """Test sync operation with metrics display."""
    with patch("tushell.tushellcli.EchoSyncClient", return_value=mock_client):
        result = runner.invoke(echo_sync, [
            "--node-id", "test-node",
            "--metrics"
        ])
        assert result.exit_code == 0
        assert "Sync Metrics" in result.output
        assert "duration_ms: 100" in result.output

def test_echo_sync_export(runner, mock_client, env_vars, tmp_path):
    """Test sync operation with export."""
    export_file = tmp_path / "sync_results.json"
    with patch("tushell.tushellcli.EchoSyncClient", return_value=mock_client):
        result = runner.invoke(echo_sync, [
            "--node-id", "test-node",
            "--export", str(export_file)
        ])
        assert result.exit_code == 0
        assert export_file.exists()
        with open(export_file) as f:
            data = json.load(f)
            assert "status" in data

def test_echo_sync_missing_env_vars(runner):
    """Test sync operation with missing environment variables."""
    result = runner.invoke(echo_sync, ["--node-id", "test-node"])
    assert result.exit_code != 0
    assert "ECHO_API_URL and ECHO_TOKEN environment variables must be set" in result.output

def test_echo_sync_api_error(runner, mock_client, env_vars):
    """Test sync operation with API error."""
    mock_client.push_state.side_effect = Exception("API Error")
    with patch("tushell.tushellcli.EchoSyncClient", return_value=mock_client):
        result = runner.invoke(echo_sync, [
            "--node-id", "test-node",
            "--action", "push",
            "--verbose"
        ])
        assert result.exit_code == 0
        assert "Error pushing data" in result.output

def test_echo_sync_with_retry(runner, mock_client, env_vars):
    """Test sync operation with retry logic."""
    mock_client.push_state.side_effect = [
        Exception("Temporary Error"),
        {"status": "success", "message": "Retry successful"}
    ]
    with patch("tushell.tushellcli.EchoSyncClient", return_value=mock_client):
        result = runner.invoke(echo_sync, [
            "--node-id", "test-node",
            "--action", "push",
            "--retry", "3"
        ])
        assert result.exit_code == 0
        assert "Data successfully pushed to remote nodes" in result.output

def test_echo_sync_with_filter(runner, mock_client, env_vars):
    """Test sync operation with node filter."""
    with patch("tushell.tushellcli.EchoSyncClient", return_value=mock_client):
        result = runner.invoke(echo_sync, [
            "--node-id", "test-node",
            "--action", "batch",
            "--filter", "node-*",
            "--verbose"
        ])
        assert result.exit_code == 0
        assert "Filter: node-*" in result.output

def test_echo_sync_with_priority(runner, mock_client, env_vars):
    """Test sync operation with priority."""
    with patch("tushell.tushellcli.EchoSyncClient", return_value=mock_client):
        result = runner.invoke(echo_sync, [
            "--node-id", "test-node",
            "--priority", "5",
            "--verbose"
        ])
        assert result.exit_code == 0
        assert "Priority: 5" in result.output 