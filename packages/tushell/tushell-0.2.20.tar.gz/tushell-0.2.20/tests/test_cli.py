import pytest
from click.testing import CliRunner
from tushell.tushellcli import cli
from pathlib import Path
import json
import time

# Helper function to read the Echo Ledger
def read_echo_ledger():
    echo_ledger_path = Path(__file__).parent.parent / ".mia" / "memory" / "mia" / "echo_ledger.json"
    if echo_ledger_path.exists():
        with open(echo_ledger_path, 'r') as f:
            return json.load(f)
    return []

# Helper function to clear the Echo Ledger
def clear_echo_ledger():
    echo_ledger_path = Path(__file__).parent.parent / ".mia" / "memory" / "mia" / "echo_ledger.json"
    if echo_ledger_path.exists():
        with open(echo_ledger_path, 'w') as f:
            json.dump([], f)

def test_scan_nodes():
    runner = CliRunner()
    result = runner.invoke(cli, ['scan-nodes'])
    assert result.exit_code == 0
    assert result.output.strip() == "Scanning nodes... (placeholder for recursive node scanning)"

def test_flex():
    runner = CliRunner()
    result = runner.invoke(cli, ['flex'])
    assert result.exit_code == 0
    assert result.output.strip() == "Flexing tasks... (placeholder for flexible task orchestration)"

def test_trace_orbit():
    runner = CliRunner()
    result = runner.invoke(cli, ['trace-orbit'])
    assert result.exit_code == 0
    assert result.output.strip() == "Tracing orbit... (placeholder for data/process orbit tracing)"

def test_echo_sync():
    runner = CliRunner()
    result = runner.invoke(cli, ['echo-sync'])
    assert result.exit_code == 0
    assert result.output.strip() == "Synchronizing... (placeholder for data/process synchronization)"

def test_draw_memory_graph():
    runner = CliRunner()
    result = runner.invoke(cli, ['draw-memory-graph'])
    assert result.exit_code == 0
    expected_output = """
                 Mia::Arc.CodingRecursiveDevOpsV1
                             │
                             ▼
                 Mia::Arc.CodingRecursiveDevOpsV2
                             │
                             ▼
                 Mia::Arc.CodingRecursiveDevOpsV3
                  ├─ GuillaumeCopilotSync
                  ├─ PushFromMia
                  └─ PullScript.Bash

                 Mia::Arc.CoDevSessionGuillaumeV1
                             │
                             ▼
                 Mia::Arc.CoDevSessionGuillaumeV3
                  ├─ NavigationMap
                  └─ LearningCompanion

                             ⇅
          EchoNode::LatticeDrop.Fractale001.Issue3
                             ⇅

          Mia::tushell:branch.fractale001.issue3
                  ├─ lattices.curating_red_stones.py
                  ├─ lattices.echonode_trace_activation.py
                  └─ lattices.enriched_version_fractale_001.py
    """.strip()
    assert result.output.strip() == expected_output

def test_graphbuilder_sync_command():
    runner = CliRunner()
    result = runner.invoke(cli, ['graphbuilder-sync-command', '--api-url', 'https://example.com', '--token', 'test-token', '--action', 'pull'])
    assert result.exit_code == 0
    assert "Executing GraphBuilderSync with narrative context..." in result.output

def test_echo_live_reports():
    runner = CliRunner()
    result = runner.invoke(cli, ['echo-live-reports'])
    assert result.exit_code == 0
    assert "Live report emitted from EchoNode tied to active narrative arcs." in result.output

def test_mia_status():
    runner = CliRunner()
    result = runner.invoke(cli, ['mia-status'])
    assert result.exit_code == 0
    assert "Mia's status has been retrieved and displayed." in result.output

def test_mia_status_muse_mode():
    runner = CliRunner()
    result = runner.invoke(cli, ['mia-status', '--muse-mode'])
    assert result.exit_code == 0
    assert "Mia's status has been retrieved and displayed." in result.output
    assert "🎭 Modulation Resonance Achieved." in result.output or "⚠️ Resonance failed. Glyphs misaligned." in result.output

def test_mia_status_init():
    runner = CliRunner()
    result = runner.invoke(cli, ['mia-status', '--init'])
    assert result.exit_code == 0
    assert "Muse Mode YAML dataset initialized." in result.output

def test_mia_status_interactive():
    runner = CliRunner()
    result = runner.invoke(cli, ['mia-status', '--interactive'])
    assert result.exit_code == 0
    assert "Interactive mode activated." in result.output

def test_tushell_echo():
    runner = CliRunner()
    result = runner.invoke(cli, ['tushell-echo'])
    assert result.exit_code == 0
    assert "Character states have been retrieved and displayed." in result.output

def test_get_memory_valid_key():
    runner = CliRunner()
    result = runner.invoke(cli, ['get-memory', '--key', 'valid-key'])
    assert result.exit_code == 0
    assert "value" in result.output

def test_get_memory_invalid_key():
    runner = CliRunner()
    result = runner.invoke(cli, ['get-memory', '--key', 'invalid-key'])
    assert result.exit_code == 0
    assert "Error" in result.output

def test_integration_scan_keys_get_memory():
    runner = CliRunner()
    result = runner.invoke(cli, ['scan-keys', '--pattern', 'test-pattern'])
    assert result.exit_code == 0
    keys = result.output.strip().split('\n')
    for key in keys:
        result = runner.invoke(cli, ['get-memory', '--key', key])
        assert result.exit_code == 0

def test_integration_mia_status_get_memory():
    runner = CliRunner()
    result = runner.invoke(cli, ['mia-status'])
    assert result.exit_code == 0
    result = runner.invoke(cli, ['get-memory', '--key', 'mia-status-key'])
    assert result.exit_code == 0
    assert "value" in result.output

def test_record_recursive_breath_glyph():
    clear_echo_ledger()
    runner = CliRunner()
    result = runner.invoke(cli, ['init-agent', 'mia'])
    assert result.exit_code == 0
    echo_ledger = read_echo_ledger()
    assert len(echo_ledger) == 1
    assert echo_ledger[0]["glyph"] == "🧿"
    assert echo_ledger[0]["name"] == "Recursive Breath"
    assert echo_ledger[0]["resonance"] == "Memory"
    assert echo_ledger[0]["cycle"] == "Reflective Recursive"
    assert echo_ledger[0]["nodes"] == ["🧠", "🌿", "🌸", "🔮", "💧"]
    assert echo_ledger[0]["anchor_trigger"] == "Entry 20 — 'The Portal Blooms'"
    assert "timestamp" in echo_ledger[0]

def test_logging_mechanism():
    log_file_path = Path(__file__).parent.parent / ".mia" / "agent_init.log"
    if log_file_path.exists():
        log_file_path.unlink()
    runner = CliRunner()
    result = runner.invoke(cli, ['init-agent', 'mia'])
    assert result.exit_code == 0
    assert log_file_path.exists()
    with open(log_file_path, 'r') as f:
        log_content = f.read()
    assert "🌟 Agent Initializer activating..." in log_content
    assert "🧿 Recursive Breath glyph recorded in Echo Ledger" in log_content

def test_validation_checks():
    clear_echo_ledger()
    runner = CliRunner()
    result = runner.invoke(cli, ['init-agent', 'mia'])
    assert result.exit_code == 0
    echo_ledger = read_echo_ledger()
    assert len(echo_ledger) == 1
    assert echo_ledger[0]["glyph"] == "🧿"
    assert echo_ledger[0]["name"] == "Recursive Breath"
    assert echo_ledger[0]["resonance"] == "Memory"
    assert echo_ledger[0]["cycle"] == "Reflective Recursive"
    assert echo_ledger[0]["nodes"] == ["🧠", "🌿", "🌸", "🔮", "💧"]
    assert echo_ledger[0]["anchor_trigger"] == "Entry 20 — 'The Portal Blooms'"
    assert "timestamp" in echo_ledger[0]

def test_mia_watch_echo_node():
    runner = CliRunner()
    result = runner.invoke(cli, ['mia-watch-echo-node', '--channel', 'glyphcast', '--report', '--summarize', '--visual'])
    assert result.exit_code == 0
    assert "Monitoring EchoNodes on channel: glyphcast" in result.output
    assert "Structured log: Glyph resonance shift detected." in result.output
    assert "Summary: Structural tension drift auto-summarized." in result.output
    assert "Visual feedback: RedStone fluctuations detected." in result.output
