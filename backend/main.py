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

# Setup Playwright
print("Initializing browser...")
playwright = sync_playwright().start()
browser = playwright.chromium.launch(headless=False)
context = browser.new_context(viewport={"width": SCREEN_WIDTH, "height": SCREEN_HEIGHT})
page = context.new_page()

# Define helper functions. Copy/paste from steps 3 and 4
def denormalize_x(x: int, screen_width: int) -> int:
    """Convert normalized x coordinate (0-1000) to actual pixel coordinate."""
    return int(x / 1000 * screen_width)

def denormalize_y(y: int, screen_height: int) -> int:
    """Convert normalized y coordinate (0-1000) to actual pixel coordinate."""
    return int(y / 1000 * screen_height)

def get_safety_confirmation(safety_decision):
    """Prompt user for confirmation when safety check is triggered."""
    termcolor.cprint("Safety service requires explicit confirmation!", color="red")
    print(safety_decision["explanation"])

    decision = ""
    while decision.lower() not in ("y", "n", "ye", "yes", "no"):
        decision = input("Do you wish to proceed? [Y]es/[N]o\n")

    if decision.lower() in ("n", "no"):
        return "TERMINATE"
    return "CONTINUE"

def execute_function_calls(candidate, page, screen_width, screen_height):
    results = []
    function_calls = []
    print(json.dumps(candidate.model_dump(), indent=2))
    for part in candidate.content.parts:
        if part.function_call:
            function_calls.append(part.function_call)

    for function_call in function_calls:
        extra_fr_fields = {}
        action_result = {}
        fname = function_call.name
        args = function_call.args
        print(f"  -> Executing: {fname}")

        # Safety confirmation: if the model included a safety_decision, prompt the user
        if 'safety_decision' in function_call.args:
            decision = get_safety_confirmation(function_call.args['safety_decision'])
            if decision == "TERMINATE":
                print("Terminating agent loop")
                break
            # Use a boolean field named 'safety_acknowledged' (server often expects this)
            # and add it to the extra fields to be merged into the action result.
            extra_fr_fields["safety_acknowledgement"] = True

        try:

            if fname == "open_web_browser":
                pass # Already open
            elif fname == "click_at":
                actual_x = denormalize_x(args["x"], screen_width)
                actual_y = denormalize_y(args["y"], screen_height)
                page.mouse.click(actual_x, actual_y)
            elif fname == "type_text_at":
                actual_x = denormalize_x(args["x"], screen_width)
                actual_y = denormalize_y(args["y"], screen_height)
                text = args["text"]
                press_enter = args.get("press_enter", False)

                page.mouse.click(actual_x, actual_y)
                # Simple clear (Command+A, Backspace for Mac)
                page.keyboard.press("Meta+A")
                page.keyboard.press("Backspace")
                page.keyboard.type(text)
                if press_enter:
                    page.keyboard.press("Enter")
            else:
                print(f"Warning: Unimplemented or custom function {fname}")

            # Wait for potential navigations/renders
            page.wait_for_load_state(timeout=5000)
            time.sleep(1)

        except Exception as e:
            print(f"Error executing {fname}: {e}")
            action_result = {"error": str(e)}

        # Merge any extra fields (like safety acknowledgement) into the action result
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
excluded_functions = ["drag_and_drop"]

generate_content_config = genai.types.GenerateContentConfig(
    tools=[
        # 1. Computer Use tool with browser environment
        types.Tool(
            computer_use=types.ComputerUse(
                environment=types.Environment.ENVIRONMENT_BROWSER,
                # Optional: Exclude specific predefined functions
                excluded_predefined_functions=excluded_functions
                )
              ),
        # 2. Optional: Custom user-defined functions
        #types.Tool(
          # function_declarations=custom_functions
          #   )
          ],
  )

try:
    # Go to initial page
    page.goto("https://www.google.com/")

    # Configure the model (From Step 1)
    config = types.GenerateContentConfig(
        tools=[types.Tool(computer_use=types.ComputerUse(
            environment=types.Environment.ENVIRONMENT_BROWSER
        ))],
        thinking_config=types.ThinkingConfig(include_thoughts=True),
    )

    # Initialize history
    initial_screenshot = page.screenshot(type="png")
    USER_PROMPT = "Go to https://q.utoronto.ca/ and log into my account using username 'minalex' and password 'earlierothermakingjungle'. Find my statistics class and read the syllabus"
    print(f"Goal: {USER_PROMPT}")

    contents = [
        Content(role="user", parts=[
            Part(text=USER_PROMPT),
            Part.from_bytes(data=initial_screenshot, mime_type='image/png')
        ])
    ]

    # Agent Loop
    turn_limit = 100
    for i in range(turn_limit):
        print(f"\n--- Turn {i+1} ---")
        print("Thinking...")
        response = generate_content_with_retries(
            client,
            model="gemini-2.5-computer-use-preview-10-2025",
            contents=contents,  # type: ignore
            config=generate_content_config,
        )

        candidate = response.candidates[0] # type: ignore
        contents.append(candidate.content) # type: ignore

        has_function_calls = any(part.function_call for part in candidate.content.parts) # type: ignore
        if not has_function_calls:
            text_response = " ".join([part.text for part in candidate.content.parts if part.text]) # type: ignore
            print("Agent finished:", text_response)
            break

        print("Executing actions...")
        results, terminated = execute_function_calls(candidate, page, SCREEN_WIDTH, SCREEN_HEIGHT)
        if terminated:
            print("Agent loop terminated by user safety decision.")
            break

        print("Capturing state...")
        function_responses = get_function_responses(page, results)

        contents.append(
            Content(role="user", parts=[Part(function_response=fr) for fr in function_responses])
        )

finally:
    # Cleanup
    print("\nClosing browser...")
    browser.close()
    playwright.stop()
