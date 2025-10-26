from browser_computer import BrowserComputer

class ActionHandler:
    def __init__(self, browser_computer: BrowserComputer, screen_width: int, screen_height: int):
        self._browser_computer = browser_computer
        self.screen_width = screen_width
        self.screen_height = screen_height

    def denormalize_x(self, x: int) -> int:
        try:
            return max(0, min(int(x / 1000 * self.screen_width), self.screen_width - 1))
        except Exception:
            return 0

    def denormalize_y(self, y: int) -> int:
        try:
            return max(0, min(int(y / 1000 * self.screen_height), self.screen_height - 1))
        except Exception:
            return 0

    def handle_action(self, action):
        """Handles the action and returns the environment state."""
        name = action.name
        args = action.args or {}

        if name == "open_web_browser":
            return self._browser_computer.open_web_browser()
        elif name == "click_at":
            try:
                x = self.denormalize_x(args["x"])
                y = self.denormalize_y(args["y"])
            except Exception:
                return {"error": "invalid click coordinates"}
            return self._browser_computer.click_at(x=x, y=y)
        elif name == "hover_at":
            try:
                x = self.denormalize_x(args["x"])
                y = self.denormalize_y(args["y"])
            except Exception:
                return {"error": "invalid hover coordinates"}
            return self._browser_computer.hover_at(x=x, y=y)
        elif name == "type_text_at":
            try:
                x = self.denormalize_x(args["x"])
                y = self.denormalize_y(args["y"])
            except Exception:
                return {"error": "invalid type coordinates"}
            press_enter = args.get("press_enter", False)
            clear_before_typing = args.get("clear_before_typing", True)
            text = args.get("text", "")
            return self._browser_computer.type_text_at(
                x=x,
                y=y,
                text=text,
                press_enter=press_enter,
                clear_before_typing=clear_before_typing,
            )
        elif name == "scroll_document":
            return self._browser_computer.scroll_document(args.get("direction", "down"))
        elif name == "scroll_at":
            try:
                x = self.denormalize_x(args["x"])
                y = self.denormalize_y(args["y"])
            except Exception:
                return {"error": "invalid scroll coordinates"}
            magnitude = args.get("magnitude", 800)
            direction = args.get("direction")
            if direction is None:
                return {"error": "missing scroll direction"}

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
            url = args.get("url")
            if not url:
                return {"error": "missing url"}
            return self._browser_computer.navigate(url)
        elif name == "key_combination":
            keys = args.get("keys")
            if not keys:
                return {"error": "missing keys"}
            return self._browser_computer.key_combination(str(keys).split("+"))
        elif name == "drag_and_drop":
            try:
                x = self.denormalize_x(args["x"])
                y = self.denormalize_y(args["y"])
                destination_x = self.denormalize_x(args["destination_x"])
                destination_y = self.denormalize_y(args["destination_y"])
            except Exception:
                return {"error": "invalid drag coordinates"}
            steps = args.get("steps", 10)
            return self._browser_computer.drag_and_drop(x=x, y=y, destination_x=destination_x, destination_y=destination_y, steps=steps)
        else:
            # Fallback for unknown actions
            raise ValueError(f"Unsupported function: {action}")