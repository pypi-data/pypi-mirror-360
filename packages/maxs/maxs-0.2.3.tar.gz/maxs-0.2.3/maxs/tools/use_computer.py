#!/usr/bin/env python3
"""Enhanced computer control tool with advanced features including scrolling,
screen switching, drag operations, and more sophisticated keyboard/mouse controls.
"""

import pyautogui
from typing import Any, Dict
from datetime import datetime
import os
import platform
import time

# Initialize pyautogui safely
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1  # Add small delay between actions for stability

TOOL_SPEC = {
    "name": "use_computer",
    "description": "Advanced computer control with mouse, keyboard, screenshots, scrolling, and screen management",
    "inputSchema": {
        "json": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [
                        # Mouse actions
                        "mouse_position",
                        "click",
                        "double_click",
                        "right_click",
                        "middle_click",
                        "move_mouse",
                        "drag",
                        "scroll",
                        # Keyboard actions
                        "type",
                        "key_press",
                        "hotkey",
                        # Screen actions
                        "screenshot",
                        "screen_size",
                        "switch_screen",
                        "switch_app",
                        # Window actions
                        "minimize_all",
                        "show_desktop",
                        "mission_control",
                        # System info
                        "get_system_info",
                    ],
                    "description": "The action to perform",
                },
                "x": {
                    "type": "integer",
                    "description": "X coordinate for mouse actions",
                },
                "y": {
                    "type": "integer",
                    "description": "Y coordinate for mouse actions",
                },
                "to_x": {
                    "type": "integer",
                    "description": "Destination X for drag operations",
                },
                "to_y": {
                    "type": "integer",
                    "description": "Destination Y for drag operations",
                },
                "text": {
                    "type": "string",
                    "description": "Text to type",
                },
                "key": {
                    "type": "string",
                    "description": "Key to press (e.g., 'enter', 'tab', 'space', 'escape')",
                },
                "keys": {
                    "type": "array",
                    "description": "List of keys for hotkey combination (e.g., ['cmd', 'a'])",
                    "items": {"type": "string"},
                },
                "clicks": {
                    "type": "integer",
                    "description": "Number of clicks for scroll action",
                    "default": 3,
                },
                "direction": {
                    "type": "string",
                    "enum": ["up", "down", "left", "right"],
                    "description": "Direction for scroll or swipe",
                },
                "region": {
                    "type": "array",
                    "description": "Optional region for screenshot [left, top, width, height]",
                    "items": {"type": "integer"},
                },
                "button": {
                    "type": "string",
                    "enum": ["left", "right", "middle"],
                    "description": "Mouse button to use (default: left)",
                    "default": "left",
                },
                "duration": {
                    "type": "number",
                    "description": "Duration in seconds for mouse movements",
                    "default": 0.5,
                },
                "interval": {
                    "type": "number",
                    "description": "Interval between keystrokes when typing",
                    "default": 0.0,
                },
                "screen_number": {
                    "type": "integer",
                    "description": "Screen number to switch to (for multi-monitor setups)",
                },
                "app_name": {
                    "type": "string",
                    "description": "Application name to switch to",
                },
            },
            "required": ["action"],
        }
    },
}


def get_platform_keys() -> Dict[str, str]:
    """Get platform-specific key mappings."""
    system = platform.system().lower()
    if system == "darwin":  # macOS
        return {
            "cmd": "command",
            "ctrl": "ctrl",
            "opt": "option",
            "alt": "option",
            "super": "command",
        }
    else:  # Windows/Linux
        return {
            "cmd": "winleft",
            "ctrl": "ctrl",
            "opt": "alt",
            "alt": "alt",
            "super": "winleft",
        }


def normalize_key(key: str) -> str:
    """Normalize key names across platforms."""
    key_map = get_platform_keys()
    return key_map.get(key.lower(), key.lower())


def use_computer(
    tool: Any,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Execute computer control actions."""
    try:
        tool_use_id = tool["toolUseId"]
        tool_input = tool["input"]
        action = tool_input["action"]
        result = {"status": "success", "toolUseId": tool_use_id}

        # Mouse position
        if action == "mouse_position":
            x, y = pyautogui.position()
            result["content"] = [{"text": f"Mouse position: ({x}, {y})"}]

        # Screenshots
        elif action == "screenshot":
            # Create screenshots directory if it doesn't exist
            screenshots_dir = os.path.expanduser("~/.agi/screenshots")
            if not os.path.exists(screenshots_dir):
                os.makedirs(screenshots_dir)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            filepath = os.path.join(screenshots_dir, filename)

            # Take screenshot with optional region
            region = tool_input.get("region")
            screenshot = (
                pyautogui.screenshot(region=tuple(region))
                if region
                else pyautogui.screenshot()
            )

            # Save locally
            screenshot.save(filepath)

            # Read the file in binary mode
            with open(filepath, "rb") as image_file:
                file_bytes = image_file.read()

            result["content"] = [
                {"text": f"Screenshot saved to {filepath}"},
                {"image": {"format": "png", "source": {"bytes": file_bytes}}},
            ]

        # Typing
        elif action == "type":
            text = tool_input.get("text")
            if not text:
                raise ValueError("No text provided for typing")
            interval = tool_input.get("interval", 0.0)
            pyautogui.typewrite(text, interval=interval)
            result["content"] = [{"text": f"Typed: {text}"}]

        # Click actions
        elif action == "click":
            x = tool_input.get("x")
            y = tool_input.get("y")
            if x is None or y is None:
                raise ValueError("Missing x or y coordinates for click")

            button = tool_input.get("button", "left")
            duration = tool_input.get("duration", 0.5)

            # Move mouse smoothly to position and click
            pyautogui.moveTo(x, y, duration=duration)
            pyautogui.click(button=button)
            result["content"] = [
                {"text": f"Clicked at ({x}, {y}) with {button} button"}
            ]

        elif action == "double_click":
            x = tool_input.get("x")
            y = tool_input.get("y")
            if x is None or y is None:
                raise ValueError("Missing x or y coordinates for double click")

            duration = tool_input.get("duration", 0.5)
            pyautogui.moveTo(x, y, duration=duration)
            pyautogui.doubleClick()
            result["content"] = [{"text": f"Double-clicked at ({x}, {y})"}]

        elif action == "right_click":
            x = tool_input.get("x")
            y = tool_input.get("y")
            if x is None or y is None:
                raise ValueError("Missing x or y coordinates for right click")

            duration = tool_input.get("duration", 0.5)
            pyautogui.moveTo(x, y, duration=duration)
            pyautogui.rightClick()
            result["content"] = [{"text": f"Right-clicked at ({x}, {y})"}]

        elif action == "middle_click":
            x = tool_input.get("x")
            y = tool_input.get("y")
            if x is None or y is None:
                raise ValueError("Missing x or y coordinates for middle click")

            duration = tool_input.get("duration", 0.5)
            pyautogui.moveTo(x, y, duration=duration)
            pyautogui.middleClick()
            result["content"] = [{"text": f"Middle-clicked at ({x}, {y})"}]

        # Mouse movement
        elif action == "move_mouse":
            x = tool_input.get("x")
            y = tool_input.get("y")
            if x is None or y is None:
                raise ValueError("Missing x or y coordinates for mouse movement")

            duration = tool_input.get("duration", 0.5)
            pyautogui.moveTo(x, y, duration=duration)
            result["content"] = [{"text": f"Moved mouse to ({x}, {y})"}]

        # Drag operation
        elif action == "drag":
            x = tool_input.get("x")
            y = tool_input.get("y")
            to_x = tool_input.get("to_x")
            to_y = tool_input.get("to_y")

            if any(coord is None for coord in [x, y, to_x, to_y]):
                raise ValueError("Missing coordinates for drag operation")

            button = tool_input.get("button", "left")
            duration = tool_input.get("duration", 1.0)

            pyautogui.moveTo(x, y, duration=0.5)
            pyautogui.dragTo(to_x, to_y, duration=duration, button=button)
            result["content"] = [
                {"text": f"Dragged from ({x}, {y}) to ({to_x}, {to_y})"}
            ]

        # Scrolling
        elif action == "scroll":
            direction = tool_input.get("direction", "down")
            clicks = tool_input.get("clicks", 3)
            x = tool_input.get("x")
            y = tool_input.get("y")

            # Move to position if specified
            if x is not None and y is not None:
                pyautogui.moveTo(x, y, duration=0.3)

            # Determine scroll amount based on direction
            if direction in ["up", "down"]:
                scroll_amount = clicks if direction == "up" else -clicks
                pyautogui.scroll(scroll_amount)
            else:  # left or right
                # Horizontal scroll (shift + scroll on most systems)
                pyautogui.keyDown("shift")
                scroll_amount = clicks if direction == "right" else -clicks
                pyautogui.scroll(scroll_amount)
                pyautogui.keyUp("shift")

            result["content"] = [{"text": f"Scrolled {direction} by {clicks} clicks"}]

        # Key press
        elif action == "key_press":
            key = tool_input.get("key")
            if not key:
                raise ValueError("No key specified for key press")
            pyautogui.press(key)
            result["content"] = [{"text": f"Pressed key: {key}"}]

        # Hotkey combination
        elif action == "hotkey":
            keys = tool_input.get("keys")
            if not keys:
                raise ValueError("No keys specified for hotkey")

            # Normalize keys for cross-platform compatibility
            normalized_keys = [normalize_key(k) for k in keys]
            pyautogui.hotkey(*normalized_keys)
            result["content"] = [{"text": f"Pressed hotkey: {' + '.join(keys)}"}]

        # Screen size
        elif action == "screen_size":
            width, height = pyautogui.size()
            result["content"] = [{"text": f"Screen size: {width}x{height}"}]

        # Switch screen (for multi-monitor setups)
        elif action == "switch_screen":
            screen_number = tool_input.get("screen_number", 1)
            system = platform.system().lower()

            if system == "darwin":  # macOS
                # Use Mission Control to switch spaces
                pyautogui.hotkey("ctrl", f"{screen_number}")
            elif system == "windows":
                # Windows + P to cycle through display modes
                pyautogui.hotkey("win", "p")
                time.sleep(0.5)
                # Press arrow keys to select display mode
                for _ in range(screen_number):
                    pyautogui.press("down")
                pyautogui.press("enter")
            else:  # Linux
                # This varies by desktop environment
                pyautogui.hotkey("super", f"{screen_number}")

            result["content"] = [{"text": f"Switched to screen {screen_number}"}]

        # Switch application
        elif action == "switch_app":
            app_name = tool_input.get("app_name")
            if not app_name:
                raise ValueError("No app name specified")

            system = platform.system().lower()

            if system == "darwin":  # macOS
                # Use Spotlight to open app
                pyautogui.hotkey("cmd", "space")
                time.sleep(0.5)
                pyautogui.typewrite(app_name)
                time.sleep(0.5)
                pyautogui.press("enter")
            elif system == "windows":
                # Use Windows search
                pyautogui.press("win")
                time.sleep(0.5)
                pyautogui.typewrite(app_name)
                time.sleep(0.5)
                pyautogui.press("enter")
            else:  # Linux
                # Use Alt+F2 or Super key depending on desktop
                pyautogui.hotkey("alt", "f2")
                time.sleep(0.5)
                pyautogui.typewrite(app_name)
                time.sleep(0.5)
                pyautogui.press("enter")

            result["content"] = [{"text": f"Switched to {app_name}"}]

        # Minimize all windows
        elif action == "minimize_all":
            system = platform.system().lower()

            if system == "darwin":  # macOS
                pyautogui.hotkey("cmd", "option", "h", "m")
            elif system == "windows":
                pyautogui.hotkey("win", "d")
            else:  # Linux
                pyautogui.hotkey("super", "d")

            result["content"] = [{"text": "Minimized all windows"}]

        # Show desktop
        elif action == "show_desktop":
            system = platform.system().lower()

            if system == "darwin":  # macOS
                pyautogui.hotkey("fn", "f11")
            elif system == "windows":
                pyautogui.hotkey("win", "d")
            else:  # Linux
                pyautogui.hotkey("super", "d")

            result["content"] = [{"text": "Showing desktop"}]

        # Mission Control (macOS) / Task View (Windows) / Activities (Linux)
        elif action == "mission_control":
            system = platform.system().lower()

            if system == "darwin":  # macOS
                pyautogui.hotkey("ctrl", "up")
            elif system == "windows":
                pyautogui.hotkey("win", "tab")
            else:  # Linux (GNOME)
                pyautogui.hotkey("super")

            result["content"] = [{"text": "Opened mission control / task view"}]

        # Get system info
        elif action == "get_system_info":
            info = {
                "platform": platform.system(),
                "screen_size": pyautogui.size(),
                "mouse_position": pyautogui.position(),
                "failsafe": pyautogui.FAILSAFE,
                "pause": pyautogui.PAUSE,
            }
            result["content"] = [{"text": f"System info: {info}"}]

        else:
            raise ValueError(f"Unknown action: {action}")

        return result

    except Exception as e:
        return {
            "status": "error",
            "toolUseId": tool_use_id,
            "content": [{"text": f"Error: {str(e)}"}],
        }
