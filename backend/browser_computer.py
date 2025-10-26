import time

class BrowserComputer:
    """Adapter around a Playwright page exposing higher-level actions."""
    def __init__(self, page):
        self.page = page
        # If page has a viewport size, use it for clamping; otherwise default
        try:
            vp = getattr(self.page, 'viewport_size', None)
            if vp and isinstance(vp, dict):
                self._width = vp.get('width', 1440)
                self._height = vp.get('height', 900)
            else:
                self._width = 1440
                self._height = 900
        except Exception:
            self._width = 1440
            self._height = 900

    def open_web_browser(self):
        return {"status": "already_open"}

    def click_at(self, x, y):
        try:
            cx = max(0, min(int(x), self._width - 1))
            cy = max(0, min(int(y), self._height - 1))
            self.page.mouse.click(cx, cy)
            return {"clicked": [cx, cy]}
        except Exception as e:
            return {"error": str(e)}

    def hover_at(self, x, y):
        try:
            hx = max(0, min(int(x), self._width - 1))
            hy = max(0, min(int(y), self._height - 1))
            self.page.mouse.move(hx, hy)
            return {"hovered": [hx, hy]}
        except Exception as e:
            return {"error": str(e)}

    def type_text_at(self, x, y, text, press_enter=False, clear_before_typing=True):
        try:
            tx = max(0, min(int(x), self._width - 1))
            ty = max(0, min(int(y), self._height - 1))
            self.page.mouse.click(tx, ty)
            if clear_before_typing:
                try:
                    self.page.keyboard.press("Meta+A")
                    self.page.keyboard.press("Backspace")
                except Exception:
                    # fallback: select-all may not exist on some platforms
                    pass
            self.page.keyboard.type(str(text))
            if press_enter:
                try:
                    self.page.keyboard.press("Enter")
                except Exception:
                    pass
            return {"typed": text}
        except Exception as e:
            return {"error": str(e)}

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
        try:
            self.page.evaluate(f"window.scrollBy({dx}, {dy})")
            return {"scrolled_by": [dx, dy]}
        except Exception as e:
            return {"error": str(e)}

    def wait_5_seconds(self):
        time.sleep(5)
        return {"waited_seconds": 5}

    def go_back(self):
        try:
            self.page.go_back()
            return {"navigated": "back"}
        except Exception as e:
            return {"error": str(e)}

    def go_forward(self):
        try:
            self.page.go_forward()
            return {"navigated": "forward"}
        except Exception as e:
            return {"error": str(e)}

    def search(self):
        # placeholder for a search helper
        return {"search": None}

    def navigate(self, url):
        try:
            self.page.goto(url)
            return {"navigated_to": url}
        except Exception as e:
            return {"error": str(e)}

    def key_combination(self, keys):
        # keys is a list like ["Control", "a"] or similar
        pressed = []
        try:
            for k in keys:
                try:
                    self.page.keyboard.press(k)
                    pressed.append(k)
                except Exception:
                    # ignore individual key failures
                    pass
            return {"pressed_keys": pressed}
        except Exception as e:
            return {"error": str(e)}

    def drag_and_drop(self, x, y, destination_x, destination_y, steps=10):
        try:
            sx = max(0, min(int(x), self._width - 1))
            sy = max(0, min(int(y), self._height - 1))
            dx = max(0, min(int(destination_x), self._width - 1))
            dy = max(0, min(int(destination_y), self._height - 1))
            self.page.mouse.move(sx, sy)
            self.page.mouse.down()
            for i in range(1, max(1, int(steps)) + 1):
                nx = sx + (dx - sx) * i / steps
                ny = sy + (dy - sy) * i / steps
                self.page.mouse.move(int(nx), int(ny))
                time.sleep(0.02)
            self.page.mouse.up()
            return {"dragged": [[sx, sy], [dx, dy]]}
        except Exception as e:
            return {"error": str(e)}