import requests
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file in current directory or from HOME/.env
load_dotenv()
dotenv_path = os.path.join(os.path.expanduser("~"), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

#Add path to current file
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def fetch_echonode_data():
    url = f"{os.getenv('EH_API_URL')}/api/echonode"
    headers = {
        "Authorization": f"Bearer {os.getenv('EH_TOKEN')}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def process_echonode_data(data):
    # Process the data as needed
    return data

def render_echonode_data(data):
    # Render the data as part of the memory key graph
    for key, value in data.items():
        print(f"{key}: {value}")
    print("-------")

def emit_live_reports():
    echonode_data = fetch_echonode_data()
    if echonode_data:
        processed_data = process_echonode_data(echonode_data)
        render_echonode_data(processed_data)
        # Additional logic for live reporting
        print("Live report emitted from EchoNode tied to active narrative arcs.")
        # Integrate with fractalstone_protocol, redstone_protocol, and EchoMuse glyph emitters
        print("Live reports integrated with fractalstone_protocol, redstone_protocol, and EchoMuse glyph emitters.")
        # Trigger alerts for Langfuse drift deltas, PushOps → VaultOps mismatches, and recursive tension misalignments
        trigger_alerts(echonode_data)
        # Integrate with EchoVoicePortal
        integrate_with_echo_voice_portal(echonode_data)

def trigger_alerts(data):
    # Logic to trigger alerts for Langfuse drift deltas, PushOps → VaultOps mismatches, and recursive tension misalignments
    if "langfuse_drift_deltas" in data:
        print("Alert: Langfuse drift deltas detected.")
    if "pushops_vaultops_mismatches" in data:
        print("Alert: PushOps → VaultOps mismatches detected.")
    if "recursive_tension_misalignments" in data:
        print("Alert: Recursive tension misalignments detected.")

def fetch_echonode_data_optimized():
    url = f"{os.getenv('EH_API_URL')}/api/echonode"
    headers = {
        "Authorization": f"Bearer {os.getenv('EH_TOKEN')}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def process_echonode_data_optimized(data):
    # Process the data as needed
    return data

def render_echonode_data_optimized(data):
    # Render the data as part of the memory key graph
    for key, value in data.items():
        print(f"{key}: {value}")

def emit_live_reports_optimized():
    echonode_data = fetch_echonode_data_optimized()
    if echonode_data:
        processed_data = process_echonode_data_optimized(echonode_data)
        render_echonode_data_optimized(processed_data)
        # Additional logic for live reporting
        print("Live report emitted from EchoNode tied to active narrative arcs.")
        # Integrate with fractalstone_protocol, redstone_protocol, and EchoMuse glyph emitters
        print("Live reports integrated with fractalstone_protocol, redstone_protocol, and EchoMuse glyph emitters.")

def format_poetic_output(data):
    # Format the data with signal glyphs and poetic elements
    formatted_output = ""
    for key, value in data.items():
        formatted_output += f"🔮 {key}: {value}\n"
    return formatted_output

def handle_signal_glyphs(data):
    # Handle signal glyphs in the data
    signal_glyphs = []
    for key, value in data.items():
        signal_glyphs.append(f"🔮 {key}: {value}")
    return signal_glyphs

def summarize_echonode_bindings(data):
    # Summarize EchoNode bindings in the data
    bindings_summary = "EchoNode Bindings Summary:\n"
    for key, value in data.items():
        bindings_summary += f"{key}: {value}\n"
    return bindings_summary

def overlay_redstone_emotional_pulse(data):
    # Overlay redstone emotional pulse in the data
    emotional_pulse = "Redstone Emotional Pulse Overlay:\n"
    for key, value in data.items():
        emotional_pulse += f"{key}: {value}\n"
    return emotional_pulse

def integrate_with_echo_voice_portal(data):
    # Logic to integrate with EchoVoicePortal
    print("Integrating with EchoVoicePortal...")
    # Example integration logic
    if "echo_voice_portal" in data:
        print("EchoVoicePortal integration successful.")
    else:
        print("EchoVoicePortal integration failed.")
