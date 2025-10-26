import os 
import sys
from pathlib import Path

# Get the project root directory (parent of backend folder)
project_root = Path(__file__).parent.parent
env_path = project_root / '.env'

from dotenv import load_dotenv

<<<<<<< HEAD
# Load environment variables from project root .env file
load_dotenv(dotenv_path=env_path)
import google.generativeai as genai
=======
# Load environment variables from a .env file
load_dotenv()
from google import genai
>>>>>>> a6a9a621c769f20d39d7ab13261796b18130cf92
from elevenlabs_utils import transcribe_audio_file
from flask import Flask, request, jsonify
from agent_runner import AgentRunner

# Initialize genai from environment to avoid embedding secrets in code.
api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    # Create a client reference for agent_runner
    client = genai
else:
    sys.exit(
        "Missing API credentials for Google GenAI.\n"
        "Set the environment variable GOOGLE_API_KEY with your API key, or configure\n"
        "the client with vertexai/project/location per the SDK docs.\n"
        "(Also: remove any hard-coded keys from source and rotate them if exposed.)"
    )

# Constants for screen dimensions
SCREEN_WIDTH = 1440
SCREEN_HEIGHT = 900

# Playwright/browser placeholders (initialized on FastAPI startup to avoid event-loop conflicts)
playwright = None
browser = None
context = None
page = None

# Specify predefined functions to exclude (optional)
excluded_functions = []

app = Flask(__name__)
# Agent will initialize Playwright and page inside its thread; do not start
# Playwright at module import time to avoid greenlet/thread issues.
agent = AgentRunner(client)

# Define helper functions. Copy/paste from steps 3 and 4
def denormalize_x(x: int, screen_width: int) -> int:
    """Convert normalized x coordinate (0-1000) to actual pixel coordinate."""
    return int(x / 1000 * screen_width)

def denormalize_y(y: int, screen_height: int) -> int:
    """Convert normalized y coordinate (0-1000) to actual pixel coordinate."""
    return int(y / 1000 * screen_height)

@app.route('/transcribe_audio', methods=['POST'])
def api_transcribe_audio():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    temp_path = f"/tmp/{file.filename}"
    file.save(temp_path)

    try:
        transcription = transcribe_audio_file(temp_path)
        
        # Queue transcription text into the agent if it's running
        if agent.running and transcription:
            agent.enqueue_command(transcription)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    return jsonify({"status": "transcribed", "text": transcription})

@app.route('/start', methods=['POST'])
def api_start():
    payload = request.get_json() or {}
    goal = payload.get('goal')
    try:
        agent.start(goal)
        return jsonify({"status": "started", "goal": goal})
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 400


@app.route('/command', methods=['POST'])
def api_command():
    if not agent.running:
        return jsonify({"error": "Agent not running"}), 400
    payload = request.get_json() or {}
    cmd = payload.get('command')
    if not cmd:
        return jsonify({"error": "missing command"}), 400
    agent.enqueue_command(cmd)
    return jsonify({"status": "queued", "command": cmd})


@app.route('/status', methods=['GET'])
def api_status():
    return jsonify({
        "running": agent.running,
        "last_results": agent.last_results,
    "current_url": (getattr(agent, "page", None).url if getattr(agent, "page", None) is not None else ""), # type: ignore
        "current_goal": agent.current_goal,
        "goals_history": agent.goals_history,
        "update_id": agent.update_id,
        "relevant_update": getattr(agent, 'relevant_update', None),
    })


@app.route('/stop', methods=['POST'])
def api_stop():
    if not agent.running:
        return jsonify({"status": "not_running"})
    agent.stop()
    return jsonify({"status": "stopped"})


@app.route('/update_goal', methods=['POST'])
def api_update_goal():
    if not agent.running:
        return jsonify({"error": "Agent not running"}), 400
    payload = request.get_json() or {}
    goal = payload.get('goal')
    if not goal:
        return jsonify({"error": "missing goal"}), 400
    agent.update_goal(goal)
    return jsonify({"status": "updated", "goal": goal})


@app.route('/debug', methods=['GET'])
def api_debug():
    """Return debugging info about the agent internals for diagnosis."""
    thread_alive = False
    try:
        t = getattr(agent, '_thread', None)
        thread_alive = bool(t is not None and getattr(t, 'is_alive', lambda: False)())
    except Exception:
        thread_alive = False

    # Build a small preview of the latest contents (texts only)
    preview = []
    try:
        for c in (agent.contents or [])[-6:]:
            # collect text parts where available
            parts = []
            for p in getattr(c, 'parts', []) or []:
                t = getattr(p, 'text', None)
                if t:
                    parts.append(t)
            preview.append({'role': getattr(c, 'role', None), 'texts': parts})
    except Exception:
        preview = []

    return jsonify({
        'running': agent.running,
        'thread_alive': thread_alive,
        'contents_len': len(agent.contents) if getattr(agent, 'contents', None) is not None else 0,
        'contents_preview': preview,
        'last_results': agent.last_results,
        'current_goal': agent.current_goal,
        'goals_history': agent.goals_history,
        'update_id': agent.update_id,
        'relevant_update': getattr(agent, 'relevant_update', None),
    'page_url': (getattr(getattr(agent, 'page', None), 'url', '') if getattr(agent, 'page', None) is not None else ''),
    })
if __name__ == "__main__":
    try:
        # Run Flask app (development server). For production, use a WSGI server.
        # Listen on 0.0.0.0 so the app is reachable from the Docker host when
        # the container publishes port 8000.
        app.run(host="0.0.0.0", port=8000)
    finally:
        print("\nClosing browser...")
        try:
            if agent and agent.running:
                agent.stop()
        except Exception:
            pass
        try:
            if browser:
                browser.close()
        except Exception:
            pass
        try:
            if playwright:
                playwright.stop()
        except Exception:
            pass
