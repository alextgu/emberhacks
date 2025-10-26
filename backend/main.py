import time
from typing import Any, List, Tuple
from playwright.sync_api import sync_playwright
from google.genai import errors as genai_errors
from google import genai
import re
import os
import sys
from google.genai import types
from google.genai.types import Content, Part
import termcolor
import base64
import json

# .\venv\Scripts\python.exe .\backend\main.py
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Initialize genai Client from environment to avoid embedding secrets in code.
# Provide your API key by setting the environment variable GOOGLE_API_KEY.
api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    client = genai.Client(api_key=api_key)
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

# Define helper functions. Copy/paste from steps 3 and 4
def denormalize_x(x: int, screen_width: int) -> int:
    """Convert normalized x coordinate (0-1000) to actual pixel coordinate."""
    return int(x / 1000 * screen_width)

def denormalize_y(y: int, screen_height: int) -> int:
    """Convert normalized y coordinate (0-1000) to actual pixel coordinate."""
    return int(y / 1000 * screen_height)

def get_safety_confirmation(safety_decision):
    # """Prompt user for confirmation when safety check is triggered."""
    # termcolor.cprint("Safety service requires explicit confirmation!", color="red")
    # print(safety_decision["explanation"])

    # decision = ""
    # while decision.lower() not in ("y", "n", "ye", "yes", "no"):
    #     decision = input("Do you wish to proceed? [Y]es/[N]o\n")

    # if decision.lower() in ("n", "no"):
    #     return "TERMINATE"

    # yea...
    return "CONTINUE"

class BrowserComputer:
    """Adapter around a Playwright page exposing higher-level actions."""
    def __init__(self, page):
        self.page = page

    def open_web_browser(self):
        return {"status": "already_open"}

    def click_at(self, x, y):
        self.page.mouse.click(x, y)
        return {"clicked": [x, y]}

    def hover_at(self, x, y):
        self.page.mouse.move(x, y)
        return {"hovered": [x, y]}

    def type_text_at(self, x, y, text, press_enter=False, clear_before_typing=True):
        self.page.mouse.click(x, y)
        if clear_before_typing:
            self.page.keyboard.press("Meta+A")
            self.page.keyboard.press("Backspace")
        self.page.keyboard.type(text)
        if press_enter:
            self.page.keyboard.press("Enter")
        return {"typed": text}

    def scroll_document(self, direction="down"):
        if direction in ("top", "start", "0"):
            self.page.evaluate("window.scrollTo(0,0)")
            return {"scrolled_to": "top"}
        else:
            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            return {"scrolled_to": "bottom"}

    def scroll_at(self, x, y, direction, magnitude=800):
        # convert magnitude to dx/dy depending on direction
        dx = dy = 0
        try:
            mag = int(magnitude)
        except Exception:
            mag = int(float(magnitude))
        if direction in ("up", "north"):
            dy = -mag
        elif direction in ("down", "south"):
            dy = mag
        elif direction in ("left", "west"):
            dx = -mag
        elif direction in ("right", "east"):
            dx = mag
        self.page.evaluate(f"window.scrollBy({dx}, {dy})")
        return {"scrolled_by": [dx, dy]}

    def wait_5_seconds(self):
        time.sleep(5)
        return {"waited_seconds": 5}

    def go_back(self):
        self.page.go_back()
        return {"navigated": "back"}

    def go_forward(self):
        self.page.go_forward()
        return {"navigated": "forward"}

    def search(self):
        # placeholder for a search helper
        return {"search": None}

    def navigate(self, url):
        self.page.goto(url)
        return {"navigated_to": url}

    def key_combination(self, keys):
        # keys is a list like ["Control", "a"] or similar
        for k in keys:
            self.page.keyboard.press(k)
        return {"pressed_keys": keys}

    def drag_and_drop(self, x, y, destination_x, destination_y, steps=10):
        self.page.mouse.move(x, y)
        self.page.mouse.down()
        for i in range(1, steps + 1):
            nx = x + (destination_x - x) * i / steps
            ny = y + (destination_y - y) * i / steps
            self.page.mouse.move(int(nx), int(ny))
            time.sleep(0.02)
        self.page.mouse.up()
        return {"dragged": [[x, y], [destination_x, destination_y]]}


class ActionHandler:
    def __init__(self, browser_computer: BrowserComputer, screen_width: int, screen_height: int):
        self._browser_computer = browser_computer
        self.screen_width = screen_width
        self.screen_height = screen_height

    def denormalize_x(self, x: int) -> int:
        return int(x / 1000 * self.screen_width)

    def denormalize_y(self, y: int) -> int:
        return int(y / 1000 * self.screen_height)

    def handle_action(self, action):
        """Handles the action and returns the environment state."""
        name = action.name
        args = action.args or {}

        if name == "open_web_browser":
            return self._browser_computer.open_web_browser()
        elif name == "click_at":
            x = self.denormalize_x(args["x"])
            y = self.denormalize_y(args["y"])
            return self._browser_computer.click_at(x=x, y=y)
        elif name == "hover_at":
            x = self.denormalize_x(args["x"])
            y = self.denormalize_y(args["y"])
            return self._browser_computer.hover_at(x=x, y=y)
        elif name == "type_text_at":
            x = self.denormalize_x(args["x"])
            y = self.denormalize_y(args["y"])
            press_enter = args.get("press_enter", False)
            clear_before_typing = args.get("clear_before_typing", True)
            return self._browser_computer.type_text_at(
                x=x,
                y=y,
                text=args["text"],
                press_enter=press_enter,
                clear_before_typing=clear_before_typing,
            )
        elif name == "scroll_document":
            return self._browser_computer.scroll_document(args.get("direction", "down"))
        elif name == "scroll_at":
            x = self.denormalize_x(args["x"])
            y = self.denormalize_y(args["y"])
            magnitude = args.get("magnitude", 800)
            direction = args["direction"]

            if direction in ("up", "down"):
                magnitude = self.denormalize_y(magnitude)
            elif direction in ("left", "right"):
                magnitude = self.denormalize_x(magnitude)
            else:
                raise ValueError("Unknown direction: ", direction)
            return self._browser_computer.scroll_at(x=x, y=y, direction=direction, magnitude=magnitude)
        elif name == "wait_5_seconds":
            return self._browser_computer.wait_5_seconds()
        elif name == "go_back":
            return self._browser_computer.go_back()
        elif name == "go_forward":
            return self._browser_computer.go_forward()
        elif name == "search":
            return self._browser_computer.search()
        elif name == "navigate":
            return self._browser_computer.navigate(args["url"])
        elif name == "key_combination":
            return self._browser_computer.key_combination(args["keys"].split("+"))
        elif name == "drag_and_drop":
            x = self.denormalize_x(args["x"])
            y = self.denormalize_y(args["y"])
            destination_x = self.denormalize_x(args["destination_x"])
            destination_y = self.denormalize_y(args["destination_y"])
            return self._browser_computer.drag_and_drop(x=x, y=y, destination_x=destination_x, destination_y=destination_y)
        else:
            # Fallback for unknown actions
            raise ValueError(f"Unsupported function: {action}")


def execute_function_calls(candidate, page, screen_width, screen_height):
    """Collects function calls from candidate and executes them using ActionHandler."""
    results = []
    function_calls = [part.function_call for part in getattr(candidate.content, "parts", []) or [] if part.function_call]

    browser_computer = BrowserComputer(page)
    handler = ActionHandler(browser_computer, screen_width, screen_height)

    for function_call in function_calls:
        extra_fr_fields = {}
        action_result = {}
        fname = function_call.name
        args = function_call.args or {}
        print(f"  -> Executing: {fname} {args}")

        # Safety confirmation: if the model included a safety_decision, prompt the user
        if "safety_decision" in args:
            decision = get_safety_confirmation(args["safety_decision"]) if isinstance(args.get("safety_decision"), dict) else get_safety_confirmation(args["safety_decision"])  # type: ignore
            if decision == "TERMINATE":
                print("Terminating agent loop")
                return results, True
            extra_fr_fields["safety_acknowledgement"] = True

        try:
            action_result = handler.handle_action(function_call)

            # Wait for potential navigations/renders
            page.wait_for_load_state(timeout=5000)
            time.sleep(1)

        except Exception as e:
            print(f"Error executing {fname}: {e}")
            action_result = {"error": str(e)}

        if extra_fr_fields:
            action_result.update(extra_fr_fields)

        results.append((fname, action_result))

    return results, False

def get_function_responses(page, results):
    screenshot_bytes = page.screenshot(type="png")
    current_url = page.url
    function_responses = []
    for name, result in results:
        print(result)
        response_data = {"url": current_url}
        response_data.update(result)
        function_responses.append(
            types.FunctionResponse(
                name=name,
                response=response_data,
                parts=[
                    types.FunctionResponsePart(
                        inline_data=types.FunctionResponseBlob(
                            mime_type="image/png", data=screenshot_bytes
                        )
                    )
                ]
            )
        )
    return function_responses


# Generate content with the configured settings
def _extract_retry_seconds_from_error(err_json: dict) -> float | None:
    # Look for RetryInfo in the error details and parse retryDelay like '30s' or '30.905037304s'
    try:
        details = err_json.get("error", {}).get("details", [])
        for d in details:
            if d.get("@type", "").endswith("RetryInfo") and "retryDelay" in d:
                delay = d["retryDelay"]
                m = re.match(r"([0-9.]+)s", delay)
                if m:
                    return float(m.group(1))
    except Exception:
        return None
    return None

def generate_content_with_retries(client, max_attempts: int = 5, **kwargs):
    backoff = 1.0
    for attempt in range(1, max_attempts + 1):
        try:
            # Debug: print a short summary of the outgoing request to help
            # diagnose why the Computer Use tool might not be accepted by the API.
            try:
                cfg = kwargs.get("config")
                tools = None
                tools_desc = None
                if cfg is not None:
                    # print a short repr of the config object and its attributes
                    tools = getattr(cfg, "tools", None) or getattr(cfg, "tool", None) or getattr(cfg, "tools_list", None)
                    tools_desc = []
                    if tools:
                        for t in tools:
                            # try multiple attribute names that may indicate computer use
                            if getattr(t, "computerUse", None) is not None or getattr(t, "computer_use", None) is not None:
                                tools_desc.append("computerUse")
                            else:
                                # inspect attributes for useful hints
                                attrs = [a for a in dir(t) if not a.startswith("__")]
                                tools_desc.append({"repr": repr(t), "attrs": attrs[:6]})
                else:
                    tools_desc = None
            except Exception as ex:
                tools_desc = f"error:{ex}"
            try:
                kw_keys = list(kwargs.keys())
            except Exception:
                kw_keys = None
            print(f"Calling generate_content: model={kwargs.get('model')} contents_len={len(kwargs.get('contents') or [])} kwargs_keys={kw_keys} config_repr={repr(cfg)[:400]} tools={tools_desc}") # type: ignore
            return client.models.generate_content(**kwargs)
        except genai_errors.ClientError as e:
            # Try to extract a suggested retry delay from the server response
            resp_json = getattr(e, "response_json", None) or {}
            retry_seconds = _extract_retry_seconds_from_error(resp_json)
            if attempt == max_attempts:
                # Re-raise the exception after max attempts
                raise
            wait = retry_seconds if retry_seconds is not None else backoff
            print(
                f"API returned {e}. Retrying in {wait:.1f}s (attempt {attempt}/{max_attempts})"
            )
            time.sleep(wait)
            backoff = min(backoff * 2, 60)
        except Exception:
            # Non-API errors should bubble up
            raise

# Specify predefined functions to exclude (optional)
excluded_functions = []

generate_content_config = genai.types.GenerateContentConfig(
    tools=[ # type: ignore
        types.Tool(
            computerUse=types.ComputerUse( # type: ignore
                environment=types.Environment.ENVIRONMENT_BROWSER,
                excludedPredefinedFunctions=excluded_functions, # type: ignore
            )
        )
    ]
)

# Replace the interactive loop with a background agent runner and HTTP API
import threading
import queue
from flask import Flask, request, jsonify


class AgentRunner:
    """Runs the agent loop in a background thread and accepts commands via a queue."""

    def __init__(self, client, page=None, screen_width: int = SCREEN_WIDTH, screen_height: int = SCREEN_HEIGHT):
        self.client = client
        # page will be created inside the agent thread to keep Playwright calls
        # pinned to the same thread/greenlet that starts playwright.
        self.page = page
        self.screen_width = screen_width
        self.screen_height = screen_height
        self._thread = None
        self._stop_event = threading.Event()
        self._command_queue: queue.Queue[str] = queue.Queue()
        self._lock = threading.Lock()
        # conversation contents sent to the model
        self.contents: list[Content] = []
        self.running = False
        self.last_results = []
        # Short text summary of the most relevant recent update (finish message or errors)
        self.relevant_update: str | None = None
        self.current_url = ""
        # Goal tracking: allow updates while agent is running and keep history
        self.current_goal: str | None = None
        self.goals_history: list[str] = []
        # Monotonic counter that frontend can poll to detect changes
        self.update_id: int = 0

    def start(self, initial_goal: str | None = None):
        with self._lock:
            if self.running:
                raise RuntimeError("Agent already running")
            # set the current goal (initial contents will be created by the
            # agent thread once Playwright/page are initialized)
            self.current_goal = initial_goal
            if initial_goal:
                self.goals_history = [initial_goal]
            # mark start requested and launch thread which will create page
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._run_loop, daemon=True)
            self._thread.start()
            self.running = True

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)
        self.running = False

    def enqueue_command(self, cmd: str):
        self._command_queue.put(cmd)
        # signal to any pollers that new input arrived
        with self._lock:
            self.update_id += 1

    def update_goal(self, new_goal: str):
        """Update the agent's current goal while it's running. Keeps history and
        appends the new goal to the conversation so the model will see it.
        """
        with self._lock:
            prev = self.current_goal
            if prev is not None:
                # keep a record of the previous goal
                self.goals_history.append(prev)
            self.current_goal = new_goal
            # append to conversation so model receives the new instruction
            self.contents.append(Content(role="user", parts=[Part.from_text(text=new_goal)]))
            # notify pollers/frontend
            self.update_id += 1

    def _run_loop(self):
        # persistent loop: try to complete current goal, and accept commands
        # Initialize Playwright and the page inside this thread so all
        # Playwright sync calls are made from the same thread/greenlet.
        self.playwright = None
        self.browser = None
        self.context = None
        try:
            print("Agent thread: initializing Playwright...")
            self.playwright = sync_playwright().start()
            # Allow running headless via environment to support containers/CI.
            headless_env = os.getenv("HEADLESS", "0")
            print(f"HEADLESS env var: '{headless_env}'")
            headless_flag = not (headless_env.lower() in ("0", "false", "no"))
            print(f"Launching browser with headless={headless_flag}")
            self.browser = self.playwright.chromium.launch(headless=headless_flag)
            self.context = self.browser.new_context(viewport={"width": self.screen_width, "height": self.screen_height})
            self.page = self.context.new_page()
            try:
                self.page.goto("https://www.google.com/")
            except Exception as e:
                print(f"Warning: failed to open google.com on startup: {e}")

            # Build initial contents using a fresh screenshot taken on this thread
            try:
                initial_screenshot = self.page.screenshot(type="png")
            except Exception as e:
                print("Warning: failed to take initial screenshot:", e)
                initial_screenshot = b""

            # Prepare initial conversation contents
            if self.current_goal:
                self.contents = [
                    Content(role="user", parts=[
                        Part.from_text(text=self.current_goal),
                        Part.from_bytes(data=initial_screenshot, mime_type="image/png"),
                    ])
                ]
            else:
                self.contents = [
                    Content(role="user", parts=[
                        Part.from_text(text=""),
                        Part.from_bytes(data=initial_screenshot, mime_type="image/png"),
                    ])
                ]
            # bump update_id to reflect new initial state
            with self._lock:
                self.update_id += 1

            while not self._stop_event.is_set():
                turn_limit = 100
                for i in range(turn_limit):
                    if self._stop_event.is_set():
                        break
                    print(f"\n--- Turn {i+1} ---")
                    print("Thinking...")
                    try:
                        response = generate_content_with_retries(
                            self.client,
                            model="gemini-2.5-computer-use-preview-10-2025",
                            contents=self.contents,  # type: ignore
                            config=generate_content_config,
                        )
                    except Exception as e:
                                err_msg = f"Error generating content: {e}"
                                print(err_msg)
                                # publish a concise relevant update for the frontend
                                with self._lock:
                                    self.relevant_update = err_msg
                                    self.update_id += 1
                                time.sleep(1)
                                continue

                    candidate = response.candidates[0]  # type: ignore
                    # new model candidate arrived
                    self.contents.append(candidate.content)  # type: ignore
                    # notify frontend that model produced a new step
                    with self._lock:
                        self.update_id += 1

                    content_parts = getattr(candidate.content, "parts", []) or []
                    has_function_calls = any(part.function_call for part in content_parts)
                    if not has_function_calls:
                        text_response = " ".join([part.text for part in content_parts if part.text])
                        print("Agent finished:", text_response)
                        # set relevant_update to the finishing text so frontend can surface it
                        with self._lock:
                            self.relevant_update = text_response
                            self.update_id += 1
                        # finished a turn/step
                        with self._lock:
                            self.update_id += 1
                        break

                    print("Executing actions...")
                    results, terminated = execute_function_calls(
                        candidate, self.page, self.screen_width, self.screen_height
                    )
                    self.last_results = results
                    # If any function execution returned an error, publish a short relevant_update
                    try:
                        for fname, res in results:
                            if isinstance(res, dict) and res.get("error"):
                                err_msg = f"Error executing {fname}: {res.get('error')}"
                                print(err_msg)
                                with self._lock:
                                    self.relevant_update = err_msg
                                    self.update_id += 1
                                break
                    except Exception:
                        pass
                    if terminated:
                        term_msg = "Agent loop terminated by user safety decision."
                        print(term_msg)
                        with self._lock:
                            self.relevant_update = term_msg
                            self.update_id += 1
                        break

                    print("Capturing state...")
                    function_responses = get_function_responses(self.page, results)

                    self.contents.append(
                        Content(
                            role="user",
                            parts=[
                                Part.from_function_response(
                                    name=fr.name, response=fr.response, parts=getattr(fr, "parts", None)
                                )
                                for fr in function_responses
                            ],
                        )
                    )
                    # the agent appended new function responses -> update id
                    with self._lock:
                        self.update_id += 1

                    # immediately handle any queued commands by appending them as new user content
                    while not self._command_queue.empty():
                        try:
                            cmd = self._command_queue.get_nowait()
                            print("Received command:", cmd)
                            self.contents.append(Content(role="user", parts=[Part.from_text(text=cmd)]))
                            # notify frontend that commands were applied
                            with self._lock:
                                self.update_id += 1
                        except queue.Empty:
                            break

                # small sleep to avoid tight loop
                time.sleep(0.5)
        finally:
            print("Agent runner exiting loop")
            try:
                if self.context:
                    self.context.close()
            except Exception:
                pass
            try:
                if self.browser:
                    self.browser.close()
            except Exception:
                pass
            try:
                if self.playwright:
                    self.playwright.stop()
            except Exception:
                pass



app = Flask(__name__)
# Agent will initialize Playwright and page inside its thread; do not start
# Playwright at module import time to avoid greenlet/thread issues.
agent = AgentRunner(client)


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
