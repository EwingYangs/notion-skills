#!/usr/bin/env python3
"""
Get Notion cookies from Chrome using CDP (Chrome DevTools Protocol)
"""
import json
import subprocess
import time
from pathlib import Path
import sys

try:
    import websocket
except ImportError:
    print("Installing websocket-client...")
    subprocess.run([sys.executable, "-m", "pip", "install", "--break-system-packages", "websocket-client"],
                   capture_output=True)
    import websocket


def get_chrome_debugging_port():
    """Get Chrome debugging port"""
    # Try to find Chrome with remote debugging enabled
    try:
        result = subprocess.run(
            ["lsof", "-i", "tcp:9222"],
            capture_output=True,
            text=True
        )
        if "chrome" in result.stdout.lower():
            return 9222
    except:
        pass
    return None


def start_chrome_with_debugging():
    """Start Chrome with remote debugging enabled"""
    chrome_paths = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
    ]

    for chrome_path in chrome_paths:
        if Path(chrome_path).exists():
            print(f"Starting Chrome with debugging on port 9222...")
            subprocess.Popen([
                chrome_path,
                "--remote-debugging-port=9222",
                "--user-data-dir=/tmp/chrome-debug",
                "https://www.notion.so/profile/templates"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(3)
            return True

    print("Chrome not found. Please install Google Chrome.")
    return False


def get_cookies_from_chrome():
    """Get cookies from Chrome via CDP"""
    port = get_chrome_debugging_port()

    if not port:
        print("Chrome debugging port not found. Starting Chrome...")
        if not start_chrome_with_debugging():
            return None
        port = 9222

    # Get list of tabs
    import urllib.request
    try:
        response = urllib.request.urlopen(f"http://localhost:{port}/json")
        tabs = json.loads(response.read())

        # Find Notion tab
        ws_url = None
        for tab in tabs:
            if "notion.so" in tab.get("url", ""):
                ws_url = tab.get("webSocketDebuggerUrl")
                break

        if not ws_url:
            print("Notion tab not found. Please open https://www.notion.so/profile/templates in Chrome")
            return None

        # Connect to WebSocket
        ws = websocket.create_connection(ws_url)

        # Get cookies
        ws.send(json.dumps({
            "id": 1,
            "method": "Network.getAllCookies"
        }))

        response = json.loads(ws.recv())
        cookies = response.get("result", {}).get("cookies", [])

        ws.close()

        return cookies

    except Exception as e:
        print(f"Error: {e}")
        return None


def main():
    print("Getting Notion cookies from Chrome...")

    cookies = get_cookies_from_chrome()

    if not cookies:
        print("\nFailed to get cookies automatically.")
        print("Please run: python scripts/save_cookies.py")
        sys.exit(1)

    # Filter Notion cookies
    notion_cookies = [c for c in cookies if "notion.so" in c.get("domain", "")]

    # Format as cookie string
    cookie_string = "; ".join([f"{c['name']}={c['value']}" for c in notion_cookies])

    # Get user_id
    user_id = ""
    for c in notion_cookies:
        if c['name'] == 'notion_user_id':
            user_id = c['value']
            break

    # Save to files
    config_dir = Path.home() / ".config" / "notion"
    config_dir.mkdir(parents=True, exist_ok=True)

    cookie_file = config_dir / "cookies.txt"
    user_id_file = config_dir / "user_id.txt"

    cookie_file.write_text(cookie_string)
    user_id_file.write_text(user_id)

    print("\n" + "=" * 80)
    print("✅ Cookies saved successfully!")
    print(f"   Cookie file: {cookie_file}")
    print(f"   User ID file: {user_id_file}")
    print(f"   User ID: {user_id}")
    print("=" * 80)


if __name__ == "__main__":
    main()
