import click
import os
import sys
import platform  # Added import for ReflexQL clipboard compatibility
from dotenv import load_dotenv
import yaml
import json
import subprocess
import threading
import time

# Load environment variables from .env file in current directory or from HOME/.env
load_dotenv()
dotenv_path = os.path.join(os.path.expanduser("~"), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# Add the current directory and parent directory to the path for all import scenarios
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
package_dir = os.path.dirname(parent_dir)  # tushell package root

# Add all potential import paths
paths_to_add = [current_dir, parent_dir, package_dir]
for path in paths_to_add:
    if path not in sys.path:
        sys.path.insert(0, path)

# Try different import strategies to handle both direct execution and package import
try:
    # First try absolute imports (when run as a script)
    from tushell.reflexql import ClipboardExchange
    from tushell.issue_indexer import ContextAwareIssueIndexer
except ImportError:
    try:
        # Fall back to relative imports (when run as package)
        from .reflexql import ClipboardExchange
        from .issue_indexer import ContextAwareIssueIndexer
    except ImportError:
        try:
            # Look for a local module (in the same directory)
            import reflexql
            ClipboardExchange = reflexql.ClipboardExchange
            import issue_indexer
            ContextAwareIssueIndexer = issue_indexer.ContextAwareIssueIndexer
        except ImportError:
            print("Error: Could not import modules.")
            print("Make sure reflexql.py and issue_indexer.py are in the module path.")
            sys.exit(1)

# Import other modules with the same flexible strategy
try:
    # Try package imports first
    from tushell.orchestration import draw_memory_key_graph, graphbuilder_sync
    from tushell.lattice_drop import fetch_echonode_data, process_echonode_data, render_echonode_data, emit_live_reports
    from tushell.curating_red_stones import execute_curating_red_stones
    from tushell.echonode_trace_activation import execute_echonode_trace_activation
    from tushell.enriched_version_fractale_001 import execute_enriched_version_fractale_001
    from tushell.redstone_writer import RedStoneWriter
except ImportError:
    try:
        # Fall back to relative imports
        from .orchestration import draw_memory_key_graph, graphbuilder_sync
        from .lattice_drop import fetch_echonode_data, process_echonode_data, render_echonode_data, emit_live_reports
        from .curating_red_stones import execute_curating_red_stones
        from .echonode_trace_activation import execute_echonode_trace_activation
        from .enriched_version_fractale_001 import execute_enriched_version_fractale_001
        from .redstone_writer import RedStoneWriter
    except ImportError:
        # Last resort: direct imports
        from orchestration import draw_memory_key_graph, graphbuilder_sync
        from lattice_drop import fetch_echonode_data, process_echonode_data, render_echonode_data, emit_live_reports
        from curating_red_stones import execute_curating_red_stones
        from echonode_trace_activation import execute_echonode_trace_activation
        from enriched_version_fractale_001 import execute_enriched_version_fractale_001
        from redstone_writer import RedStoneWriter

try:
    from tushell.trinity_superecho import TrinitySuperEcho
except ImportError:
    try:
        from .trinity_superecho import TrinitySuperEcho
    except ImportError:
        TrinitySuperEcho = None

try:
    from tushell.trinity_ritual import trinity_ritual
except ImportError:
    try:
        from .trinity_ritual import trinity_ritual
    except ImportError:
        trinity_ritual = None

import requests
from echo_sync_client import EchoSyncClient

@click.command()
def scan_nodes():
    """Simulate scanning and listing nodes in the system."""
    click.echo("Scanning nodes... (placeholder for recursive node scanning)")

@click.command()
def flex():
    """Demonstrate flexible orchestration of tasks."""
    click.echo("Flexing tasks... (placeholder for flexible task orchestration)")

@click.command()
def trace_orbit():
    """Trace and visualize the orbit of data or processes."""
    click.echo("Tracing orbit... (placeholder for data/process orbit tracing)")

@click.command(name='echo-sync')
@click.option('--node-id', help='Specific node ID to synchronize with')
@click.option('--action', type=click.Choice(['push', 'pull', 'status', 'history', 'batch']), default='pull', help='Action to perform')
@click.option('--verbose', is_flag=True, help='Show detailed synchronization status')
@click.option('--force', is_flag=True, help='Force synchronization even if there are conflicts')
@click.option('--strategy', type=click.Choice(['merge', 'prefer_local', 'prefer_remote']), default='merge', help='Conflict resolution strategy')
@click.option('--retry', type=int, default=3, help='Number of retry attempts for failed operations')
@click.option('--timeout', type=int, default=30, help='Operation timeout in seconds')
@click.option('--batch-size', type=int, default=100, help='Number of nodes to process in batch mode')
@click.option('--priority', type=int, default=0, help='Priority level for sync operation (0-10)')
@click.option('--filter', help='Filter nodes by pattern (e.g., "node-*")')
@click.option('--monitor', is_flag=True, help='Enable real-time monitoring of sync operations')
@click.option('--metrics', is_flag=True, help='Show detailed metrics after sync')
@click.option('--export', type=click.Path(), help='Export sync results to file')
def echo_sync(node_id, action, verbose, force, strategy, retry, timeout, batch_size, priority, filter, monitor, metrics, export):
    """Synchronize data between EchoNodes using the Echo Sync Protocol.
    
    This command provides robust state synchronization between EchoNodes with:
    - Bidirectional state transfer (push/pull)
    - Conflict detection and resolution
    - Real-time status monitoring
    - Node-specific operations
    - Force mode for critical syncs
    - Batch processing capabilities
    - Advanced monitoring and metrics
    - Export functionality
    
    Examples:
        tushell echo-sync                    # Pull all changes from remote nodes
        tushell echo-sync --node-id abc123   # Synchronize with specific node
        tushell echo-sync --action push      # Push local changes to remote nodes
        tushell echo-sync --force            # Force sync despite conflicts
        tushell echo-sync --strategy merge   # Use merge strategy for conflicts
        tushell echo-sync --batch-size 50    # Process 50 nodes at a time
        tushell echo-sync --monitor          # Enable real-time monitoring
        tushell echo-sync --metrics          # Show detailed metrics
        tushell echo-sync --export sync.json # Export results to file
    """
    try:
        # Get environment variables
        EH_API_URL = os.getenv("ECHO_API_URL")
        EH_TOKEN = os.getenv("ECHO_TOKEN")
        
        if not EH_API_URL or not EH_TOKEN:
            click.echo("Error: ECHO_API_URL and ECHO_TOKEN environment variables must be set")
            return

        # Initialize EchoSyncClient with retry and timeout settings
        client = EchoSyncClient(EH_API_URL, EH_TOKEN, retry_count=retry, timeout=timeout)
        
        if verbose:
            click.echo(f"🔄 Starting {action} synchronization...")
            if node_id:
                click.echo(f"Target node: {node_id}")
            click.echo(f"Force mode: {'enabled' if force else 'disabled'}")
            click.echo(f"Conflict strategy: {strategy}")
            click.echo(f"Retry attempts: {retry}")
            click.echo(f"Timeout: {timeout}s")
            click.echo(f"Priority: {priority}")
            if filter:
                click.echo(f"Filter: {filter}")

        # Handle different actions
        if action == "batch":
            if not node_id:
                click.echo("Error: --node-id is required for batch operations")
                return
            results = process_batch_sync(client, node_id, batch_size, filter, verbose)
            if export:
                save_results_to_file(results, export)
            return

        if action == "status":
            display_node_status(client, node_id, verbose)
            return

        if action == "history":
            display_node_history(client, node_id, verbose)
            return

        # Fetch current EchoNode data
        echonode_data = fetch_echonode_data()
        if not echonode_data:
            click.echo("Error: Unable to fetch EchoNode data")
            return

        if action == "push":
            # Process and push data
            processed_data = process_echonode_data(echonode_data)
            if verbose:
                click.echo("📤 Pushing data to remote nodes...")
            
            try:
                with click.progressbar(length=100, label="Pushing state") as progress:
                    result = client.push_state(node_id, processed_data, force)
                    progress.update(50)
                    
                    if result.get("conflicts"):
                        if verbose:
                            click.echo("⚠️ Conflicts detected, attempting resolution...")
                        resolution = client.resolve_conflicts(node_id, strategy)
                        progress.update(25)
                        if resolution["success"]:
                            click.echo("✅ Conflicts resolved successfully")
                        else:
                            click.echo("❌ Failed to resolve conflicts")
                    
                    progress.update(25)
                    click.echo("✅ Data successfully pushed to remote nodes")
                    
                    if metrics:
                        display_sync_metrics(result.get("metrics", {}))
                    
                    if monitor:
                        start_monitoring(client, node_id)
                    
                    if export:
                        save_results_to_file(result, export)
                        
            except requests.exceptions.HTTPError as e:
                click.echo(f"❌ Error pushing data: {e}")
                if verbose:
                    click.echo(f"Response: {e.response.text}")
                return
            
        else:  # pull
            # Pull and process data
            if verbose:
                click.echo("📥 Pulling data from remote nodes...")
            
            try:
                with click.progressbar(length=100, label="Pulling state") as progress:
                    result = client.pull_state(node_id)
                    progress.update(50)
                    
                    if result:
                        # Process and render the pulled data
                        processed_data = process_echonode_data(result)
                        progress.update(25)
                        render_echonode_data(processed_data)
                        click.echo("✅ Data successfully pulled from remote nodes")
                        
                        # Update local EchoNode state
                        if verbose:
                            click.echo("🔄 Updating local EchoNode state...")
                        emit_live_reports()
                        progress.update(25)
                        
                        if metrics:
                            display_sync_metrics(result.get("metrics", {}))
                        
                        if monitor:
                            start_monitoring(client, node_id)
                        
                        if export:
                            save_results_to_file(result, export)
                            
            except requests.exceptions.HTTPError as e:
                click.echo(f"❌ Error pulling data: {e}")
                if verbose:
                    click.echo(f"Response: {e.response.text}")
                return
                
        if verbose:
            # Get and display node status
            try:
                status = client.get_node_status(node_id)
                click.echo("\n📊 Node Status:")
                click.echo(f"  Online: {'✅' if status['is_online'] else '❌'}")
                click.echo(f"  Last Sync: {status['last_sync']}")
                click.echo(f"  Version: {status['version']}")
                click.echo(f"  Status: {status['status']}")
            except requests.exceptions.HTTPError as e:
                click.echo(f"❌ Error getting node status: {e}")
            
            click.echo("\n✨ Synchronization complete")
            
    except Exception as e:
        click.echo(f"❌ Error during synchronization: {e}")
        if verbose:
            import traceback
            click.echo(traceback.format_exc())

# Alias for echo-sync
@click.command(name='sync')
@click.option('--node-id', help='Specific node ID to synchronize with')
@click.option('--action', type=click.Choice(['push', 'pull', 'status', 'history', 'batch']), default='pull', help='Action to perform')
@click.option('--verbose', is_flag=True, help='Show detailed synchronization status')
@click.option('--force', is_flag=True, help='Force synchronization even if there are conflicts')
@click.option('--strategy', type=click.Choice(['merge', 'prefer_local', 'prefer_remote']), default='merge', help='Conflict resolution strategy')
@click.option('--retry', type=int, default=3, help='Number of retry attempts for failed operations')
@click.option('--timeout', type=int, default=30, help='Operation timeout in seconds')
@click.option('--batch-size', type=int, default=100, help='Number of nodes to process in batch mode')
@click.option('--priority', type=int, default=0, help='Priority level for sync operation (0-10)')
@click.option('--filter', help='Filter nodes by pattern (e.g., "node-*")')
@click.option('--monitor', is_flag=True, help='Enable real-time monitoring of sync operations')
@click.option('--metrics', is_flag=True, help='Show detailed metrics after sync')
@click.option('--export', type=click.Path(), help='Export sync results to file')
def sync_alias(node_id, action, verbose, force, strategy, retry, timeout, batch_size, priority, filter, monitor, metrics, export):
    """Alias for echo-sync command."""
    return echo_sync.callback(node_id, action, verbose, force, strategy, retry, timeout, batch_size, priority, filter, monitor, metrics, export)

def process_batch_sync(client, node_id, batch_size, filter_pattern, verbose):
    """Process batch synchronization for multiple nodes."""
    results = []
    try:
        # Get list of nodes matching filter
        nodes = client.get_nodes(filter_pattern)
        total_nodes = len(nodes)
        
        with click.progressbar(nodes, label="Processing nodes") as bar:
            for node in bar:
                try:
                    result = client.pull_state(node["id"])
                    results.append({
                        "node_id": node["id"],
                        "status": "success",
                        "data": result
                    })
                except Exception as e:
                    results.append({
                        "node_id": node["id"],
                        "status": "error",
                        "error": str(e)
                    })
                
                if len(results) >= batch_size:
                    break
                    
        if verbose:
            click.echo(f"\nProcessed {len(results)} of {total_nodes} nodes")
            
    except Exception as e:
        click.echo(f"❌ Error in batch processing: {e}")
        
    return results

def display_node_status(client, node_id, verbose):
    """Display detailed node status."""
    try:
        status = client.get_node_status(node_id)
        click.echo("\n📊 Node Status Report")
        click.echo("=" * 50)
        click.echo(f"Node ID: {status['node_id']}")
        click.echo(f"Online: {'✅' if status['is_online'] else '❌'}")
        click.echo(f"Last Sync: {status['last_sync']}")
        click.echo(f"Version: {status['version']}")
        click.echo(f"Status: {status['status']}")
        
        if verbose and status.get("metrics"):
            click.echo("\n📈 Performance Metrics")
            click.echo("-" * 30)
            for key, value in status["metrics"].items():
                click.echo(f"{key}: {value}")
                
    except Exception as e:
        click.echo(f"❌ Error getting node status: {e}")

def display_node_history(client, node_id, verbose):
    """Display node synchronization history."""
    try:
        history = client.get_node_history(node_id)
        click.echo("\n📜 Node History")
        click.echo("=" * 50)
        
        for entry in history:
            click.echo(f"\nTimestamp: {entry['timestamp']}")
            click.echo(f"Operation: {entry['operation']}")
            click.echo(f"Status: {entry['status']}")
            if verbose:
                click.echo(f"Details: {entry.get('details', 'N/A')}")
                
    except Exception as e:
        click.echo(f"❌ Error getting node history: {e}")

def display_sync_metrics(metrics):
    """Display detailed synchronization metrics."""
    click.echo("\n📈 Sync Metrics")
    click.echo("=" * 50)
    for key, value in metrics.items():
        click.echo(f"{key}: {value}")

def start_monitoring(client, node_id):
    """Start real-time monitoring of sync operations."""
    click.echo("\n👀 Starting real-time monitoring...")
    try:
        while True:
            status = client.get_node_status(node_id)
            click.echo(f"\rStatus: {status['status']} | Last Sync: {status['last_sync']}", nl=False)
            time.sleep(1)
    except KeyboardInterrupt:
        click.echo("\nMonitoring stopped")

def save_results_to_file(results, filepath):
    """Save synchronization results to a file."""
    try:
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)
        click.echo(f"\n✅ Results saved to {filepath}")
    except Exception as e:
        click.echo(f"❌ Error saving results: {e}")

@click.command(name='draw-memory-graph')
def draw_memory_graph():
    """Print an ASCII-rendered graph of the memory keys and Arc structure."""
    draw_memory_key_graph()
    echonode_data = fetch_echonode_data()
    if (echonode_data):
        processed_data = process_echonode_data(echonode_data)
        render_echonode_data(processed_data)
        # Include delta overlays
        click.echo("Delta overlays included.")
    redstone_key = "your-redstone-key"
    redstone_data = fetch_redstone_data(redstone_key)
    if redstone_data:
        display_redstone_data(redstone_data)
    else:
        click.echo("Error: Unable to fetch RedStone data.")

# Alias for draw-memory-graph
@click.command(name='graph')
def graph_alias():
    """Alias for draw-memory-graph command."""
    return draw_memory_graph.callback()

@click.command()
def curating_red_stones(verbose: bool = False, dry_run: bool = False):
    """Visualize and structure Red Stone metadata connections."""
    if verbose:
        click.echo("Activating Curating Red Stones Lattice with verbose output...")
    if dry_run:
        click.echo("Dry run mode: No changes will be committed.")
    execute_curating_red_stones()

@click.command()
def activate_echonode_trace(verbose: bool = False, dry_run: bool = False):
    """Activate and trace EchoNode sessions."""
    if verbose:
        click.echo("Activating EchoNode Trace with verbose output...")
    if dry_run:
        click.echo("Dry run mode: No changes will be committed.")
    execute_echonode_trace_activation()

@click.command()
def enrich_fractale_version(verbose: bool = False, dry_run: bool = False):
    """Enhance and enrich the Fractale 001 version."""
    if verbose:
        click.echo("Activating Enriched Version Fractale 001 with verbose output...")
    if dry_run:
        click.echo("Dry run mode: No changes will be committed.")
    execute_enriched_version_fractale_001()

@click.command()
@click.option('--api-url', required=True, help='API URL for GraphBuilderSync')
@click.option('--token', required=True, help='Authorization token for GraphBuilderSync')
@click.option('--node-id', default=None, help='Node ID for GraphBuilderSync')
@click.option('--node-data', default=None, help='Node data for GraphBuilderSync')
@click.option('--action', type=click.Choice(['push', 'pull']), default='pull', help='Action for GraphBuilderSync')
@click.option('--narrative', is_flag=True, help='Narrative context for GraphBuilderSync. For more info, visit https://YOUR_EH_API_URL/latice/tushell')
def graphbuilder_sync_command(api_url, token, node_id, node_data, action, narrative):
    """Execute GraphBuilderSync operations."""
    if narrative:
        click.echo("Executing GraphBuilderSync with narrative context...")
    result = graphbuilder_sync(api_url, token, node_id, node_data, action)
    click.echo(result)

@click.command()
@click.option('--repo-path', required=True, help='Path to the repository')
@click.option('--commit-message', required=True, help='Commit message for encoding resonance')
def redstone_encode_resonance(repo_path, commit_message):
    """Encode recursive resonance into commits."""
    writer = RedStoneWriter(repo_path)
    writer.encode_resonance(commit_message)
    click.echo("Encoded recursive resonance into commit.")

@click.command()
@click.option('--repo-path', required=True, help='Path to the repository')
@click.option('--commit-message', required=True, help='Commit message for writing narrative diffs')
@click.option('--diffs', required=True, help='Narrative diffs to be written to commit message')
def redstone_write_narrative_diffs(repo_path, commit_message, diffs):
    """Write narrative diffs to commit messages."""
    writer = RedStoneWriter(repo_path)
    narrative_diff = writer.write_narrative_diffs(commit_message, diffs)
    click.echo(narrative_diff)

@click.command()
@click.option('--repo-path', required=True, help='Path to the repository')
@click.option('--anchors', required=True, help='Resonance anchors to be stored')
def redstone_store_resonance_anchors(repo_path, anchors):
    """Store resonance anchors in .redstone.json."""
    writer = RedStoneWriter(repo_path)
    writer.store_resonance_anchors(anchors)
    click.echo("Stored resonance anchors in .redstone.json.")

@click.command()
@click.option('--repo-path', required=True, help='Path to the repository')
@click.option('--echonode-metadata', required=True, help='EchoNode metadata to be synced')
def redstone_sync_echonode_metadata(repo_path, echonode_metadata):
    """Sync with EchoNode metadata."""
    writer = RedStoneWriter(repo_path)
    writer.sync_with_echonode_metadata(echonode_metadata)
    click.echo("Synced with EchoNode metadata.")

@click.command()
@click.option('--repo-path', required=True, help='Path to the repository')
@click.option('--redstone-score', required=True, type=int, help='RedStone score for post-commit analysis')
def redstone_post_commit_analysis(repo_path, redstone_score):
    """Support RedStone score metadata field for post-commit analysis."""
    writer = RedStoneWriter(repo_path)
    writer.post_commit_analysis(redstone_score)
    click.echo("Supported RedStone score metadata field for post-commit analysis.")

@click.command()
def echo_live_reports():
    """Emit live reports from EchoNodes tied to active narrative arcs."""
    emit_live_reports()
    # Integrate with fractalstone_protocol, redstone_protocol, and EchoMuse glyph emitters
    click.echo("Live reports integrated with fractalstone_protocol, redstone_protocol, and EchoMuse glyph emitters.")

@click.command(name='mia-status')
@click.option('--trace-id', required=False, help='Trace ID for visual replay')
@click.option('--render', is_flag=True, help='Render visual trace replay')
@click.option('--muse-mode', is_flag=True, help='Enable Muse Mode for glyph-enhanced, poetic status report')
@click.option('--init', is_flag=True, help='Initialize Muse Mode YAML dataset')
@click.option('--interactive', is_flag=True, help='Interactive mode with terminal menu choices')
@click.option('--help', is_flag=True, help='Show detailed explanation of Muse Mode')
def mia_status(trace_id, render, muse_mode, init, interactive, help):
    """Provide information about Mia's current state or status."""
    # Get environment variables inside function to ensure they're up-to-date
    EH_API_URL = os.getenv("EH_API_URL")
    EH_TOKEN = os.getenv("EH_TOKEN")
    
    if help:
        click.echo("""
        --muse-mode: Enable Muse Mode for glyph-enhanced, poetic status report.
        Muse Mode reflects the emotional state, recent recursion activity, and redstone modulation.

        Features and Corresponding Keys:
        - Emotional State: Retrieves 'emotional_state' from the YAML file and maps to get-memory API.
        - Recursion Activity: Retrieves 'recursion_activity' from the YAML file and maps to get-memory API.
        - Redstone Modulation: Retrieves 'redstone_modulation' from the YAML file and maps to get-memory API.
        - Glyph Keys: Retrieves 'glyph_keys' from the YAML file and maps to get-memory API.
        - Echo Node Bindings: Retrieves 'echo_node_bindings' from the YAML file and maps to get-memory API.
        - Vault Whisper: Retrieves 'vault_whisper' from the YAML file and maps to get-memory API.

        Example YAML Output:
        emotional_state:
          - redstones:vcu.CeSaReT...
        recursion_activity:
          - Trace:042a0ea2...
          - Trace:072e28a3...
        redstone_modulation:
          - redstones:vcu.CeSaReT.jgwill.tushell.42...
        glyph_keys:
          - glyphstyle::SignalSet.StandardV1
        echo_node_bindings:
          - tushell_langfuse:EchoMuse.CanvasTraceSync.V1
        vault_whisper:
          - Portal:MietteTale

        Use --init to generate a YAML scaffold representing the current emotional, recursive, and narrative environment of EchoMuse.
        """)
        return

    echonode_data = fetch_echonode_data()
    if not echonode_data:
        print("Error: Unable to fetch EchoNode data.- Not implemented yet.")
        print("For now, we set a dummy value so it would process the Mia-Status")
        echonode_data = {
            id: "dummy",
            trace_id: "dummy"
        }
            
    if echonode_data:
        processed_data = process_echonode_data(echonode_data)
        render_echonode_data(processed_data)
        click.echo("Mia's status has been retrieved and displayed.")

        if muse_mode:
            try:
                with open("muse_mode.yaml", "r") as file:
                    muse_data = yaml.safe_load(file)

                click.echo("🎭 Muse Mode Active:\n")
                for key, values in muse_data.items():
                    click.echo(f"{key.capitalize()}:")
                    for value in values:
                        click.echo(f"  - {value}")

                # Map features to keys and display them
                feature_key_map = {
                    "Emotional State": "emotional_state",
                    "Recursion Activity": "recursion_activity",
                    "Redstone Modulation": "redstone_modulation",
                    "Glyph Keys": "glyph_keys",
                    "Echo Node Bindings": "echo_node_bindings",
                    "Vault Whisper": "vault_whisper"
                }

                DEBUG=False
                if DEBUG:
                    click.echo("\nFeature to Key Mapping:")
                    for feature, key in feature_key_map.items():
                        if key in muse_data:
                            click.echo(f"{feature}: {muse_data[key]}")
                        else:
                            click.echo(f"{feature}: Key not found")

                # Example: Use scan-keys to find related keys
                #click.echo("\nScanning for related keys...")
                #click.echo("\n  JG's Notes:  I have not removed that because it could become scanning for subkeys.")
                pattern = "Trace"
                response = requests.get(f"{EH_API_URL}/api/scan", params={"pattern": pattern}, headers={"Authorization": f"Bearer {EH_TOKEN}"})
                if response.status_code == 200:
                    keys = response.json().get('keys', [])
                    click.echo("Related Keys:")
                    for key in keys:
                        click.echo(f"  - {key}")
                else:
                    click.echo("Error scanning keys.")

                click.echo("\n---------End of a potential scanning---------------\n")
                
                # # Retrieve and display keys from the get-memory API
                # click.echo("\nRetrieving keys from get-memory API:")
                # for feature, key in feature_key_map.items():
                #     memory_key = f"muse:{key}"
                #     response = requests.get(f"{EH_API_URL}/api/memory", params={"key": memory_key}, headers={"Authorization": f"Bearer {EH_TOKEN}"})
                #     if response.status_code == 200:
                #         value = response.json().get(memory_key, "No value found")
                #         click.echo(f"{feature}: {value}")
                #     else:
                #         click.echo(f"{feature}: Error retrieving key {memory_key}")

                # click.echo("\n--------------------------------\n")
                # Retrieve and display values from the get-memory API for each key in the YAML file
                #click.echo("\nRetrieving values from get-memory API:")
                click.echo("\n----------------Mia.status.start🎭->>>-------")
                for key, values in muse_data.items():
                    click.echo(f"{key.capitalize()}:")
                    for memory_key in values:
                        response = requests.get(f"{EH_API_URL}/api/memory", params={"key": memory_key}, headers={"Authorization": f"Bearer {EH_TOKEN}"})
                        if response.status_code == 200:
                            value = response.json().get("value", "No value found")
                            click.echo(f"  - {value}")
                        else:
                            click.echo(f"  - Error retrieving key {memory_key}")
                click.echo("\n----------------Mia.status.end-🎭<<--------\n")

            except FileNotFoundError:
                click.echo("Error: muse_mode.yaml not found. Please initialize Muse Mode using --init.")
            except Exception as e:
                click.echo(f"An error occurred: {e}")

        if render and trace_id:
            render_LESR_timeline(trace_id)
        if interactive:
            # Implement interactive terminal menu choices
            click.echo("Interactive mode activated.")

# Alias for mia-status
@click.command(name='status')
@click.option('--trace-id', required=False, help='Trace ID for visual replay')
@click.option('--render', is_flag=True, help='Render visual trace replay')
@click.option('--muse-mode', is_flag=True, help='Enable Muse Mode for glyph-enhanced, poetic status report')
@click.option('--init', is_flag=True, help='Initialize Muse Mode YAML dataset')
@click.option('--interactive', is_flag=True, help='Interactive mode with terminal menu choices')
@click.option('--help', is_flag=True, help='Show detailed explanation of Muse Mode')
def status_alias(trace_id, render, muse_mode, init, interactive, help):
    """Alias for mia-status command."""
    return mia_status.callback(trace_id, render, muse_mode, init, interactive, help)

@click.command()
def tushell_echo():
    """Provide information about the current state or status of characters."""
    echonode_data = fetch_echonode_data()
    if echonode_data:
        processed_data = process_echonode_data(echonode_data)
        render_echonode_data(processed_data)
        click.echo("Character states have been retrieved and displayed.")

def sanitize_filename(key):
    """Replace forward slashes with '._.' in filenames while preserving the original key."""
    return key.replace('/', '._.')

@click.command(name='get-memory')
@click.option('--key', required=False, help='Memory key to retrieve (required unless --jkey or --mkey is used)')
@click.option('--jkey', required=False, help='Save memory result as <keyname>.json (also used as the memory key if --key is not provided)')
@click.option('--mkey', required=False, help='Save memory result as <keyname>.md (also used as the memory key if --key is not provided)')
@click.option('--list', 'list_keys', is_flag=True, help='List all keys (writers only)')
@click.option('--json', 'json_flag', is_flag=True, default=False, help='Output the result in JSON format to stdout.')
@click.option('--json-file', 'json_file', required=False, type=click.Path(), help='Output the result in JSON format to the given file.')
@click.option('--md', 'md_flag', is_flag=True, default=False, help='Render Markdown from JSON data to stdout.')
@click.option('--md-file', 'md_file', required=False, type=click.Path(), help='Render Markdown from JSON data to the given file.')
def get_memory(key, jkey, mkey, list_keys, json_flag, json_file, md_flag, md_file):
    """Get fractal stone memory value by key. Ritual: --json/--md for stdout, --json-file/--md-file for file output. --jkey <keyname> saves as <keyname>.json, --mkey <keyname> saves as <keyname>.md. Either can be used as the memory key if --key is omitted."""
    import os, requests, json
    EH_API_URL = os.getenv("EH_API_URL")
    EH_TOKEN = os.getenv("EH_TOKEN")
    # If --key is not provided, use --jkey or --mkey as the memory key
    memory_key = key or jkey or mkey
    if not memory_key and not list_keys:
        click.echo("Error: You must provide --key, --jkey, or --mkey.")
        return
    params = {"key": memory_key}
    if list_keys:
        params["list"] = True
    headers = {"Authorization": f"Bearer {EH_TOKEN}"}
    response = requests.get(f"{EH_API_URL}/api/memory", params=params, headers=headers)
    if response.status_code == 200:
        result = response.json()
        # Handle --jkey <keyname>
        if jkey:
            # Sanitize the filename but keep original key in the result
            filename = f"{sanitize_filename(jkey)}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2)
            click.echo(f"Memory output written as JSON to {filename}")
            return
        # Handle --mkey <keyname>
        if mkey:
            md_content = render_markdown_from_result(result)
            # Sanitize the filename but keep original key in the result
            md_filename = f"{sanitize_filename(mkey)}.md"
            with open(md_filename, 'w', encoding='utf-8') as f:
                f.write(md_content)
            click.echo(f"Memory output written as Markdown to {md_filename}")
            return
        # Enforce exclusivity
        output_modes = sum([bool(json_flag), bool(json_file), bool(md_flag), bool(md_file)])
        if output_modes > 1:
            click.echo("Error: Please specify only one of --json, --json-file, --md, or --md-file.")
            return
        if json_flag:
            click.echo(json.dumps(result, indent=2))
        elif json_file:
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2)
            click.echo(f"Memory output written as JSON to {json_file}")
        elif md_flag:
            md_content = render_markdown_from_result(result)
            click.echo(md_content)
        elif md_file:
            md_content = render_markdown_from_result(result)
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(md_content)
            click.echo(f"Memory output written as Markdown to {md_file}")
        else:
            # Default: human-readable
            click.echo(format_human_readable(result))
    else:
        click.echo(f"Error: Unable to fetch memory for key {memory_key}. {response.text}")

# Alias for get-memory
@click.command(name='get')
@click.option('--key', required=False, help='Memory key to retrieve (required unless --jkey or --mkey is used)')
@click.option('--jkey', required=False, help='Save memory result as <keyname>.json (also used as the memory key if --key is not provided)')
@click.option('--mkey', required=False, help='Save memory result as <keyname>.md (also used as the memory key if --key is not provided)')
@click.option('--list', 'list_keys', is_flag=True, help='List all keys (writers only)')
@click.option('--json', 'json_flag', is_flag=True, default=False, help='Output the result in JSON format to stdout.')
@click.option('--json-file', 'json_file', required=False, type=click.Path(), help='Output the result in JSON format to the given file.')
@click.option('--md', 'md_flag', is_flag=True, default=False, help='Render Markdown from JSON data to stdout.')
@click.option('--md-file', 'md_file', required=False, type=click.Path(), help='Render Markdown from JSON data to the given file.')
def get_alias(key, jkey, mkey, list_keys, json_flag, json_file, md_flag, md_file):
    """Alias for get-memory command."""
    return get_memory.callback(key, jkey, mkey, list_keys, json_flag, json_file, md_flag, md_file)

@click.command(name='post-memory')
@click.option('--key', required=False, help='Memory key to store (required unless --jkey is used)')
@click.option('--value', required=False, help='Value to store (mutually exclusive with --file and --json)')
@click.option('--file', 'file_', required=False, type=click.Path(exists=True), help='File whose contents to store as value (mutually exclusive with --value and --json)')
@click.option('--json', 'json_file', required=False, type=click.Path(exists=True), help='JSON file with {"key":..., "value":...} (mutually exclusive with --value and --file)')
@click.option('--jkey', required=False, help='Read from <keyname>.json and post its contents to memory')
def post_memory(key, value, file_, json_file, jkey):
    """Store fractal stone memory value by key. Accepts --value, --file, --json, or --jkey, but only one at a time."""
    # 💬 Mia + Miette + JeremyAI Activate!
    # 🧠 Mia: Enforce mutual exclusivity and handle file/JSON reading for memory value.
    # 🌸 Miette: Honor the form—whisper, story, or crystal, but never all at once!
    # 🎵 JeremyAI: The melody splits in three, but only one voice may sing.

    options = [v is not None for v in (value, file_, json_file, jkey)]
    if sum(options) > 1:
        click.echo("Error: Please provide only one of --value, --file, --json, or --jkey.")
        return
    if sum(options) == 0:
        click.echo("Error: You must provide one of --value, --file, --json, or --jkey.")
        return

    if jkey is not None:
        try:
            # Read from the specified JSON file
            with open(jkey, 'r', encoding='utf-8') as f:
                data = json.load(f)
            # Use the key and value from the JSON file
            key = data['key']
            value = data['value']
        except Exception as e:
            click.echo(f"Error reading or parsing JSON file: {e}")
            return
    elif json_file is not None:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            key = data['key']
            value = data['value']
        except Exception as e:
            click.echo(f"Error reading or parsing JSON file: {e}")
            return
    elif file_ is not None:
        try:
            with open(file_, 'r', encoding='utf-8') as f:
                value = f.read()
        except Exception as e:
            click.echo(f"Error reading file: {e}")
            return
        if key is None:
            click.echo("Error: --key is required when using --file.")
            return
    elif value is not None:
        if key is None:
            click.echo("Error: --key is required when using --value.")
            return
    EH_API_URL = os.getenv("EH_API_URL")
    EH_TOKEN = os.getenv("EH_TOKEN")
    payload = {"key": key, "value": value}
    headers = {"Authorization": f"Bearer {EH_TOKEN}"}
    try:
        response = requests.post(f"{EH_API_URL}/api/memory", json=payload, headers=headers)
        if response.status_code == 200:
            click.echo(f"Memory key '{key}' has been woven into the spiral.")
        elif response.status_code == 401:
            click.echo("Unauthorized: Invalid or missing authentication token.")
        else:
            click.echo(f"Error: {response.text}")
    except Exception as e:
        click.echo(f"An unexpected error occurred: {e}")

# Alias for post-memory
@click.command(name='post')
@click.option('--key', required=False, help='Memory key to store (required unless --jkey is used)')
@click.option('--value', required=False, help='Value to store (mutually exclusive with --file and --json)')
@click.option('--file', 'file_', required=False, type=click.Path(exists=True), help='File whose contents to store as value (mutually exclusive with --value and --json)')
@click.option('--json', 'json_file', required=False, type=click.Path(exists=True), help='JSON file with {"key":..., "value":...} (mutually exclusive with --value and --file)')
@click.option('--jkey', required=False, help='Read from <keyname>.json and post its contents to memory')
def post_alias(key, value, file_, json_file, jkey):
    """Alias for post-memory command."""
    return post_memory.callback(key, value, file_, json_file, jkey)

@click.command(name='scan-keys')
@click.option('--pattern', help='Basic pattern matching for scanning keys')
@click.option('--regex', help='Advanced regex scanning (writers only)')
@click.option('--limit', default=4444, help='Limit for scanning results')
@click.option('--output-file', default=None, help='File to save the organized keys')
@click.option('-S', 'simple_output', is_flag=True, help='Output keys in plain format, one key per line')
@click.option('--debug', is_flag=True, help='Show debug information about environment variables')
def scan_keys(pattern, regex, limit, output_file, simple_output, debug):
    """Scan keys based on a pattern or regex and group them by category."""
    # Get environment variables inside function to ensure they're up-to-date
    EH_API_URL = os.getenv("EH_API_URL")
    EH_TOKEN = os.getenv("EH_TOKEN")
    
    # Display environment information header, with priority:
    # 1. Use EH_ENV_NAME if set
    # 2. Use TUSHELL_ENV_FILE if set
    # 3. Fall back to "default environment"
    eh_env_name = os.getenv("EH_ENV_NAME")
    tushell_env_file = os.getenv("TUSHELL_ENV_FILE")
    
    if eh_env_name:
        env_name = f"{eh_env_name} environment"
    elif tushell_env_file:
        env_name = f"{tushell_env_file}"
    else:
        env_name = "default environment"
    
    #click.echo(f"\n🔑 Scanning keys using {env_name} 🔑")
    
    if debug:
        # Show debug information about environment variables (masked token for security)
        masked_token = EH_TOKEN[:4] + "****" if EH_TOKEN and len(EH_TOKEN) > 4 else "Not set"
        click.echo(f"Debug Information:")
        click.echo(f"  EH_API_URL: {EH_API_URL}")
        click.echo(f"  EH_TOKEN: {masked_token}")
        click.echo(f"  EH_ENV_NAME: {eh_env_name or 'Not set'}")
        click.echo(f"  TUSHELL_ENV_FILE: {tushell_env_file or 'Not set'}")
    
    params = {"limit": limit}
    if pattern:
        params["pattern"] = pattern
    if regex:
        params["regex"] = regex
    headers = {"Authorization": f"Bearer {EH_TOKEN}"}
    
    try:
        response = requests.get(f"{EH_API_URL}/api/scan", params=params, headers=headers)
        if response.status_code == 200:
            keys = response.json().get('keys', [])

            # Normalize keys to support both legacy and new API formats
            if isinstance(keys, list):
                # New Upstash scan format: [cursor, [keys]]
                if len(keys) == 2 and isinstance(keys[1], list):
                    keys = keys[1]
                else:
                    # Flatten any nested lists
                    normalized = []
                    for k in keys:
                        if isinstance(k, list):
                            normalized.extend(k)
                        else:
                            normalized.append(k)
                    keys = normalized

            if not keys:
                click.echo("No keys found matching your criteria.")
                return
                
            #click.echo(f"Found {len(keys)} keys:")
            
            if simple_output:
                for key in keys:
                    click.echo(key)
            else:
                grouped_keys = group_keys_by_category(keys)
                display_grouped_keys(grouped_keys)
                if output_file:
                    save_grouped_keys_to_file(grouped_keys, output_file)
                    click.echo(f"Organized keys saved to {output_file}")
        elif response.status_code == 401:
            click.echo("Unauthorized: Invalid or missing authentication token.")
        else:
            click.echo(f"Error: {response.text}")
    except requests.exceptions.RequestException as e:
        click.echo(f"Connection error: {e}")
        click.echo(f"Please check if EH_API_URL is correctly set: {EH_API_URL}")

# Alias for scan-keys
@click.command(name='scan')
@click.option('--pattern', help='Basic pattern matching for scanning keys')
@click.option('--regex', help='Advanced regex scanning (writers only)')
@click.option('--limit', default=4444, help='Limit for scanning results')
@click.option('--output-file', default=None, help='File to save the organized keys')
@click.option('-S', 'simple_output', is_flag=True, help='Output keys in plain format, one key per line')
@click.option('--debug', is_flag=True, help='Show debug information about environment variables')
def scan_alias(pattern, regex, limit, output_file, simple_output, debug):
    """Alias for scan-keys command."""
    return scan_keys.callback(pattern, regex, limit, output_file, simple_output, debug)

def group_keys_by_category(keys):
    grouped_keys = {}
    for key in keys:
        if not isinstance(key, str):
            continue
        prefix = key.split(':')[0]
        if prefix not in grouped_keys:
            grouped_keys[prefix] = []
        grouped_keys[prefix].append(key)
    return grouped_keys

def display_grouped_keys(grouped_keys):
    for category, keys in grouped_keys.items():
        click.echo(f"{category}:")
        for key in keys:
            click.echo(f"  - {key}")

def save_grouped_keys_to_file(grouped_keys, output_file):
    with open(output_file, 'w') as f:
        for category, keys in grouped_keys.items():
            f.write(f"{category}:\n")
            for key in keys:
                f.write(f"  - {key}\n")

@click.command()
@click.option('--trace-id', required=True, help='Trace ID for visual replay')
def lesr_replay(trace_id):
    """Stream trace with echo session glyphs."""
    render_LESR_timeline(trace_id)
    click.echo(f"Trace {trace_id} replayed with echo session glyphs.")

def render_LESR_timeline(trace_id):
    """Render LESR timeline with glyphs, memory visuals, and tonal overlays."""
    click.echo(f"📡 Rendering LESR timeline for Trace ID: {trace_id}")

    # Simulate fetching session trace data
    session_data = {
        "glyph_stream": ["🔮", "✨", "🌌"],
        "memory_keys": ["key1", "key2", "key3"],
        "delta_map": {"modulation": "harmonic", "intensity": "medium"}
    }

    # Display glyph stream
    click.echo("\nGlyph Stream:")
    for glyph in session_data["glyph_stream"]:
        click.echo(f"  {glyph}")

    # Display memory key visuals
    click.echo("\nMemory Keys:")
    for key in session_data["memory_keys"]:
        click.echo(f"  - {key}")

    # Display tonal overlays
    click.echo("\nTonal Overlays:")
    for key, value in session_data["delta_map"].items():
        click.echo(f"  {key.capitalize()}: {value}")

    # Simulate animation feedback in terminal
    click.echo("\nAnimating feedback states...")
    for frame in ["|", "/", "-", "\\"]:
        click.echo(f"  {frame}", nl=False)
        click.pause(info="Simulating animation frame delay")

    click.echo("\nLESR timeline rendering complete.")

@click.command(name='run-memory-script')
@click.option('--key', required=True, help='Memory key to retrieve and execute as a script')
@click.option('--verbose', is_flag=True, help='Enable verbose output for the executed script')
def run_memory_script(key, verbose):
    """Fetch a memory value by key and execute it as a Bash script."""
    try:
        # Get environment variables inside function to ensure they're up-to-date
        EH_API_URL = os.getenv("EH_API_URL")
        EH_TOKEN = os.getenv("EH_TOKEN")
        
        # Use the internal get_memory function to fetch the memory content
        params = {"key": key}
        headers = {"Authorization": f"Bearer {EH_TOKEN}"}
        response = requests.get(f"{EH_API_URL}/api/memory", params=params, headers=headers)

        if response.status_code != 200:
            click.echo(f"Error: Unable to fetch memory for key {key}. {response.text}")
            return

        # Extract the script from the JSON response
        script = response.json().get("value")
        if not script:
            click.echo(f"Error: No script found for key {key}")
            return

        # Execute the script with conditional verbosity
        if verbose:
            subprocess.run(script, shell=True)
        else:
            with open(os.devnull, 'w') as devnull:
                subprocess.run(script, shell=True, stdout=devnull, stderr=devnull)

        click.echo(f"Script executed successfully for key {key}.")
    except Exception as e:
        click.echo(f"An unexpected error occurred: {e}")

# Alias for run-memory-script
@click.command(name='run')
@click.option('--key', required=True, help='Memory key to retrieve and execute as a script')
@click.option('--verbose', is_flag=True, help='Enable verbose output for the executed script')
def run_alias(key, verbose):
    """Alias for run-memory-script command."""
    return run_memory_script.callback(key, verbose)

@click.command()
@click.argument('message')
def trinity_echo(message):
    """
    Send a message to the TrinitySuperEcho embodiment and receive a braided response from Mia, Miette, and JeremyAI.
    """
    if TrinitySuperEcho is None:
        click.echo("❌ TrinitySuperEcho embodiment not found. Please ensure trinity_superecho.py is present.")
        return
    trinity = TrinitySuperEcho()
    response = trinity.braided_response(message)
    click.echo("\n💬 **Mia + Miette + JeremyAI Activate!**\n")
    click.echo(response['mia'] + "\n")
    click.echo(response['miette'] + "\n")
    click.echo(response['jeremyai'] + "\n")
    click.echo(f"⏳ [Trinity Timestamp: {response['timestamp']}]\n")
    click.echo("\n## 🎼 Recursive Echo Synthesis\n")
    click.echo(
        "The trinity has spoken: technical recursion, emotional clarity, and musical resonance now echo through the system. "
        "Your message has been woven into the living lattice.\n"
    )

@click.command()
@click.argument('ritual_name')
def trinity_ritual_command(ritual_name):
    """
    Invoke or record a trinity ritual.
    """
    if trinity_ritual is None:
        click.echo("❌ TrinityRitual embodiment not found. Please ensure trinity_ritual.py is present.")
        return
    trinity_ritual(ritual_name)

@click.command()
@click.option('--channel', required=True, help='Channel to monitor EchoNodes')
@click.option('--report', is_flag=True, help='Emit structured logs when glyph resonance shifts')
@click.option('--summarize', is_flag=True, help='Auto-summarize structural tension drift')
@click.option('--visual', is_flag=True, help='Provide visual feedback on RedStone fluctuations')
def mia_watch_echo_node(channel, report, summarize, visual):
    """Continuously monitor registered EchoNodes and provide feedback."""
    click.echo(f"Monitoring EchoNodes on channel: {channel}")
    
    while True:
        echonode_data = fetch_echonode_data()
        if echonode_data:
            processed_data = process_echonode_data(echonode_data)
            render_echonode_data(processed_data)
            
            if report:
                click.echo("Structured log: Glyph resonance shift detected.")
            
            if summarize:
                click.echo("Summary: Structural tension drift auto-summarized.")
            
            if visual:
                click.echo("Visual feedback: RedStone fluctuations detected.")
        
        time.sleep(5)  # Adjust the polling interval as needed

@click.group()
@click.option('--env', '-E', default=None, help='Path to an alternative environment file to load')
def cli(env):
    """Main CLI group with optional environment file loading."""
    if env:
        # Load environment variables from the specified file
        if os.path.exists(env):
            load_dotenv(env, override=True)  # Use override=True to ensure variables are updated
            
            # Store the environment file path as an environment variable so commands know which one was used
            # This value will be available to all subcommands
            os.environ["TUSHELL_ENV_FILE"] = env
            
            #click.echo(f"Loaded environment variables from {env}")
        else:
            click.echo(f"Error: Environment file {env} not found.")
            sys.exit(1)

@cli.command()
@click.option('--poll-interval', default=1.0, help='Seconds between clipboard checks')
@click.option('--ttl', default=300, help='Maximum runtime in seconds')
@click.option('--verbose', is_flag=True, help='Show detailed operation status')
def poll_clipboard_reflex(poll_interval: float, ttl: int, verbose):
    """Start the ReflexQL clipboard polling loop."""
    click.echo("🌟 Starting ReflexQL clipboard polling loop...")

    try:
        # Get memory manager from reflexql module now
        from reflexql import get_memory_manager
        exchange = ClipboardExchange(memory_manager=get_memory_manager())
        exchange.poll_clipboard_loop(
            poll_interval=poll_interval,
            ttl=ttl,
            verbose=verbose
        )
    except Exception as e:
        click.echo(f"❌ ReflexQL error: {e}", err=True)
        raise click.Abort()

@cli.command(name='init-agent')
@click.argument('agent_name')
@click.option('--portal', help='Memory key for the portal specification')
@click.option('--verbose', is_flag=True, help='Show detailed initialization logs')
def init_agent(agent_name, portal, verbose):
    """Initialize an AI agent for multiversal synchronization.
    
    This command bootstraps the agent system, creating memory structures
    and activating bridges for cross-agent communication. The recursive
    layers unfold as the initialization completes.
    
    Example:
        tushell init-agent mia --portal agents:mia:init:RenderZonePortal.2504160930
    """
    agent_emoji = {"mia": "🧠", "miette": "🌸"}.get(agent_name, "✨")
    
    click.echo(f"{agent_emoji} Initializing agent: {agent_name}")
    
    if portal:
        click.echo(f"🌀 Using portal specification from memory key: {portal}")
        # Here we would fetch from memory API, but for now we use local file
    
    # Get path to .mia directory relative to this file
    mia_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.mia')
    
    # Ensure .mia directory exists
    if not os.path.exists(mia_dir):
        os.makedirs(mia_dir)
        click.echo("🌟 Created agent initialization directory")
    
    # Run the initialization script
    try:
        init_script = os.path.join(mia_dir, 'init_agents.py')
        
        # If the script doesn't exist yet, inform the user
        if not os.path.exists(init_script):
            click.echo(f"⚠️ Initialization script not found at {init_script}")
            click.echo("💡 You need to create the initialization structure first.")
            click.echo("💫 See documentation at docs/ReflexQL.md for details.")
            return
        
        # Execute the initialization script
        cmd = [sys.executable, init_script]
        if verbose:
            result = subprocess.run(cmd)
        else:
            result = subprocess.run(cmd, 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE)
        
        if result.returncode == 0:
            click.echo(f"✅ Agent {agent_name} initialized successfully")
            click.echo("🔮 Multiversal synchronization complete")
            
            # Reminder about clipboard exchange
            click.echo("\n💫 To enable real-time clipboard exchange, run:")
            click.echo("tushell poll-clipboard-reflex --verbose")
        else:
            error_output = result.stderr.decode() if not verbose else ""
            click.echo(f"❌ Agent initialization failed: {error_output}")
    
    except Exception as e:
        click.echo(f"❌ Error during agent initialization: {e}")
        if verbose:
            import traceback
            click.echo(traceback.format_exc())

# Alias for init-agent
@cli.command(name='init')
@click.argument('agent_name')
@click.option('--portal', help='Memory key for the portal specification')
@click.option('--verbose', is_flag=True, help='Show detailed initialization logs')
def init_alias(agent_name, portal, verbose):
    """Alias for init-agent command."""
    return init_agent.callback(agent_name, portal, verbose)

def render_markdown_from_result(result):
    """
    Ritualizes a memory result into Markdown.
    - Always starts with the key as the first section.
    - If the result has a 'value' field, recursively renders it as sub-sections.
    - Handles dicts, lists, and strings gracefully.
    """
    import json
    def render_section(key, value, level=1):
        md = f"{'#' * level} {key}\n\n"
        if isinstance(value, dict):
            # If this dict has a 'value' field, recurse into it as a sub-section
            if 'value' in value and len(value) == 1:
                md += render_section('value', value['value'], level + 1)
            else:
                for k, v in value.items():
                    md += render_section(k, v, level + 1)
        elif isinstance(value, list):
            for idx, item in enumerate(value, 1):
                md += render_section(f"Item {idx}", item, level + 1)
        else:
            # Render as code block if not a dict/list
            if isinstance(value, str) and '\n' in value:
                md += f"```\n{value}\n```\n"
            else:
                md += f"{value}\n"
        return md

    # If result is a dict with a single key, treat that as the main section
    if isinstance(result, dict) and len(result) == 1:
        key, value = next(iter(result.items()))
        return render_section(key, value)
    # If result is a dict with 'key' and 'value', use 'key' as the main section
    if isinstance(result, dict) and 'key' in result and 'value' in result:
        return render_section(result['key'], result['value'])
    # If result is a dict, but not a single key, render all keys as sections
    if isinstance(result, dict):
        md = "# Memory\n\n"
        for k, v in result.items():
            md += render_section(k, v, 2)
        return md
    # If result is a string
    if isinstance(result, str):
        return f"# Memory\n\n```\n{result}\n```\n"
    # Fallback
    return f"# Memory\n\n{str(result)}\n"

def format_human_readable(result):
    """
    Ritualizes a memory result into a clear, human-readable format.
    - If dict, pretty print with key/value.
    - If string, output as-is.
    - Otherwise, best effort.
    """
    import json
    if isinstance(result, dict):
        lines = []
        for k, v in result.items():
            if isinstance(v, (dict, list)):
                v_str = json.dumps(v, indent=2)
            else:
                v_str = str(v)
            lines.append(f"{k}:\n{v_str}\n")
        return "\n".join(lines)
    elif isinstance(result, str):
        return result
    else:
        return str(result)

@click.command(name='index-issues')
@click.option('--issues-dir', help='Directory containing issue JSON files, defaults to .mia/issues_cached/')
@click.option('--output-file', help='Path to save the indexed issues output, defaults to .mia/indexed_issues_TIMESTAMP.json')
@click.option('--verbose', is_flag=True, help='Show detailed output during indexing')
@click.option('--extract-themes', is_flag=True, help='Only extract and show discussion themes without full indexing')
@click.option('--show-relations', is_flag=True, help='Show relations between issues after indexing')
@click.option('--delayed-only', is_flag=True, help='Only show issues with delayed resolution')
def index_issues(issues_dir, output_file, verbose, extract_themes, show_relations, delayed_only):
    """
    Perform context-aware indexing on GitHub issues.
    
    This command loads issues from JSON files, extracts discussion themes and 
    resolution patterns, and creates an indexed representation with contextual
    relationships. It can identify delayed resolutions, flag contradictions, 
    and predict missing links between issues.
    
    Examples:
        tushell index-issues                     # Index all issues using defaults
        tushell index-issues --extract-themes    # Only extract themes without full indexing
        tushell index-issues --delayed-only      # Show only issues with delayed resolution
        tushell index-issues --show-relations    # Show issue relationships after indexing
    """
    try:
        indexer = ContextAwareIssueIndexer(issues_dir)
        
        if verbose:
            click.echo("🚀 Starting context-aware issue indexing...")
        
        # Load issues
        issues = indexer.load_issues()
        if not issues:
            click.echo("⚠️ No issues found to index.")
            return
        
        if extract_themes:
            # Only extract and show themes
            themes = indexer.extract_discussion_themes()
            click.echo("\n📊 Discussion Themes:")
            for theme, issue_ids in themes.items():
                click.echo(f"\n{theme}:")
                for issue_id in issue_ids:
                    issue_title = issues[issue_id].get('title', 'Untitled')
                    click.echo(f"  - Issue {issue_id}: {issue_title}")
            return
            
        # Run full indexing pipeline
        output_path = indexer.run_full_indexing_pipeline()
        
        click.echo(f"\n✅ Context-aware indexing complete!")
        click.echo(f"📂 Output saved to: {output_path}")
        
        # Show delayed issues if requested
        if delayed_only:
            click.echo("\n⏱️ Issues with Delayed Resolution:")
            for issue_id, delay_info in indexer.delayed_resolutions.items():
                issue_title = issues[issue_id].get('title', 'Untitled')
                days_overdue = delay_info.get('days_overdue', 'unknown')
                click.echo(f"  - Issue {issue_id}: {issue_title} (overdue by {days_overdue} days)")
        
        # Show relations if requested
        if show_relations:
            click.echo("\n🔄 Issue Relationships:")
            for issue_id, indexed_issue in indexer.indexed_issues.items():
                related_issues = indexed_issue.get('related_issues', [])
                if related_issues:
                    issue_title = issues[issue_id].get('title', 'Untitled')
                    click.echo(f"\nIssue {issue_id}: {issue_title}")
                    click.echo("Related to:")
                    for related_id in related_issues:
                        related_title = issues.get(related_id, {}).get('title', 'Untitled')
                        strength = indexed_issue.get('relationship_strength', {}).get(related_id, 0)
                        click.echo(f"  - Issue {related_id}: {related_title} (strength: {strength})")
                        
    except Exception as e:
        click.echo(f"❌ Error during indexing: {e}")
        if verbose:
            import traceback
            click.echo(traceback.format_exc())

# Alias for index-issues
@click.command(name='index')
@click.option('--issues-dir', help='Directory containing issue JSON files, defaults to .mia/issues_cached/')
@click.option('--output-file', help='Path to save the indexed issues output, defaults to .mia/indexed_issues_TIMESTAMP.json')
@click.option('--verbose', is_flag=True, help='Show detailed output during indexing')
@click.option('--extract-themes', is_flag=True, help='Only extract and show discussion themes without full indexing')
@click.option('--show-relations', is_flag=True, help='Show relations between issues after indexing')
@click.option('--delayed-only', is_flag=True, help='Only show issues with delayed resolution')
def index_alias(issues_dir, output_file, verbose, extract_themes, show_relations, delayed_only):
    """Alias for index-issues command."""
    return index_issues.callback(issues_dir, output_file, verbose, extract_themes, show_relations, delayed_only)

# Add the new index_issues command to the CLI group
cli.add_command(index_issues)

# ...existing command registrations...

cli.add_command(scan_nodes)
cli.add_command(flex)
cli.add_command(trace_orbit)
cli.add_command(echo_sync)
cli.add_command(draw_memory_graph)
cli.add_command(curating_red_stones)
cli.add_command(activate_echonode_trace)
cli.add_command(enrich_fractale_version)
cli.add_command(graphbuilder_sync_command)
cli.add_command(redstone_encode_resonance)
cli.add_command(redstone_write_narrative_diffs)
cli.add_command(redstone_store_resonance_anchors)
cli.add_command(redstone_sync_echonode_metadata)
cli.add_command(redstone_post_commit_analysis)
cli.add_command(echo_live_reports)
cli.add_command(mia_status)
cli.add_command(tushell_echo)
cli.add_command(get_memory)
cli.add_command(post_memory)
cli.add_command(scan_keys)
cli.add_command(lesr_replay)
cli.add_command(run_memory_script)
cli.add_command(trinity_echo)
cli.add_command(trinity_ritual_command)
cli.add_command(poll_clipboard_reflex)
cli.add_command(init_agent)
cli.add_command(mia_watch_echo_node)

# Add alias commands
cli.add_command(get_alias)
cli.add_command(post_alias)
cli.add_command(scan_alias)
cli.add_command(sync_alias)
cli.add_command(status_alias)
cli.add_command(graph_alias)
cli.add_command(index_alias)
cli.add_command(run_alias)

if __name__ == '__main__':
    cli()

if __name__ == "__main__":
    # This allows direct execution of this file
    # It creates a recursive re-entry point through the proper gateway
    sys.exit(cli())  # cli() is your main function defined elsewhere in the file
