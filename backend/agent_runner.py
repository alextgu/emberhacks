import os 
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from project root
project_root = Path(__file__).parent.parent
env_path = project_root / '.env'
load_dotenv(dotenv_path=env_path)

import time
from typing import Any, List, Tuple
from playwright.sync_api import sync_playwright
from google.genai import errors as genai_errors
from google import genai
import re
from google.genai import types
from google.genai.types import Content, Part
import termcolor
import base64
import json
from elevenlabs_utils import transcribe_audio_file 
from flask import Flask, request, jsonify
from browser_computer import BrowserComputer
from action_handler import ActionHandler
import threading
import queue

# default excluded functions list (can be overridden by main if needed)
excluded_functions = []

# Constants for screen dimensions
SCREEN_WIDTH = 1440
SCREEN_HEIGHT = 900

# Playwright/browser placeholders (initialized on FastAPI startup to avoid event-loop conflicts)
playwright = None
browser = None
context = None
page = None

generate_content_config = genai.types.GenerateContentConfig(
    tools=[  # type: ignore
        types.Tool(
            computerUse=types.ComputerUse(  # type: ignore
                environment=types.Environment.ENVIRONMENT_BROWSER,
                excludedPredefinedFunctions=excluded_functions,  # type: ignore
            )
        )
    ]
)

def get_function_responses(page, results):
    # take a screenshot if possible; failures shouldn't crash the agent
    try:
        screenshot_bytes = page.screenshot(type="png")
    except Exception as e:
        print("Warning: failed to capture screenshot:", e)
        screenshot_bytes = b""
    try:
        current_url = page.url
    except Exception:
        current_url = ""
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

def execute_function_calls(candidate, page, screen_width, screen_height):
    """Collects function calls from candidate and executes them using ActionHandler."""
    results = []
    # Safely collect any function_call parts (guard against None/malformed parts)
    parts = getattr(candidate.content, "parts", []) or []
    function_calls = [getattr(part, "function_call") for part in parts if getattr(part, "function_call", None)]

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
        # when True the agent is idle (finished its work) and will wait for new goals
        self.idle = False
        # event used to wake the agent from idle state when a new goal arrives
        self._wake_event = threading.Event()
        # Monotonic counter that frontend can poll to detect changes
        self.update_id = 0

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
        # Reset the agent's conversation to only include the newest goal so
        # the model focuses on the new instruction. Wake the agent if it was idle.
        screenshot_bytes = b""
        try:
            # try to capture a fresh screenshot if the page is available
            p = getattr(self, 'page', None)
            if p is not None and hasattr(p, 'screenshot'):
                try:
                    screenshot_bytes = p.screenshot(type="png")
                except Exception:
                    screenshot_bytes = b""
        except Exception:
            screenshot_bytes = b""

        with self._lock:
            prev = self.current_goal
            # only append previous goal if it's different from the new one
            if prev is not None and prev != new_goal:
                self.goals_history.append(prev)
            self.current_goal = new_goal
            # reset conversation contents to only the new goal (and screenshot)
            parts = [Part.from_text(text=new_goal)]
            if screenshot_bytes:
                parts.append(Part.from_bytes(data=screenshot_bytes, mime_type="image/png"))
            self.contents = [Content(role="user", parts=parts)]
            # mark agent as active (wake) and bump update id
            self.idle = False
            self._wake_event.set()
            self.update_id += 1

    def _set_relevant_update(self, msg: str | None):
        """Set a short, de-duplicated relevant_update and bump update_id.

        This prevents repeating the same long message and keeps the field size bounded.
        """
        if msg is None:
            return
        try:
            s = str(msg).strip()
        except Exception:
            s = ""
        if not s:
            return
        # cap length to avoid huge repeated strings
        max_len = 1000
        if len(s) > max_len:
            s = s[: max_len - 3] + "..."
        with self._lock:
            if self.relevant_update == s:
                return
            self.relevant_update = s
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
                                self._set_relevant_update(err_msg)
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
                        self._set_relevant_update(text_response)
                        # mark idle and wait until a new goal wakes the agent
                        with self._lock:
                            self.idle = True
                        # clear any previous wake event then wait (wake by update_goal)
                        self._wake_event.clear()
                        # wait until wake or stop; timeout to re-check stop_event periodically
                        while not self._stop_event.is_set():
                            # wait returns True if event is set
                            if self._wake_event.wait(timeout=1.0):
                                break
                        # woke up -> continue outer loop to handle new goal
                        with self._lock:
                            self.idle = False
                        continue

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
                                self._set_relevant_update(err_msg)
                                break
                    except Exception:
                        pass
                    if terminated:
                        term_msg = "Agent loop terminated by user safety decision."
                        print(term_msg)
                        self._set_relevant_update(term_msg)
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