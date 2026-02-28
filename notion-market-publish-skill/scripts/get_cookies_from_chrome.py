#!/usr/bin/env python3
"""
Get cookies from user's existing Chrome browser
Connects to Chrome via CDP (Chrome DevTools Protocol)
"""
from pathlib import Path
import json
import subprocess
import sys


def get_chrome_cookies():
    """Get cookies from existing Chrome browser"""
    print("🔍 Looking for Chrome browser...")

    # Check if Chrome is running with debugging port
    try:
        result = subprocess.run(
            ["lsof", "-i", "tcp:9222"],
            capture_output=True,
            text=True,
            timeout=5
        )

        if "chrome" not in result.stdout.lower():
            print("\n❌ Chrome is not running with remote debugging enabled.")
            print("\n📝 Please start Chrome with debugging:")
            print("   1. Close all Chrome windows")
            print("   2. Run this command:")
            print('      /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --remote-debugging-port=9222 &')
            print("   3. Navigate to: https://www.notion.so/profile/templates")
            print("   4. Login if needed")
            print("   5. Run this script again")
            return None, None

    except Exception as e:
        print(f"❌ Error checking Chrome: {e}")
        return None, None

    print("✅ Found Chrome with debugging enabled")

    # Get tabs from Chrome
    import urllib.request
    try:
        response = urllib.request.urlopen("http://localhost:9222/json")
        tabs = json.loads(response.read())

        print(f"📑 Found {len(tabs)} open tabs")

        # Find Notion tab
        notion_tab = None
        for tab in tabs:
            url = tab.get("url", "")
            if "notion.so" in url:
                notion_tab = tab
                print(f"✅ Found Notion tab: {url[:60]}...")
                break

        if not notion_tab:
            print("\n⚠️  No Notion tab found.")
            print("   Please open https://www.notion.so/profile/templates in Chrome")
            return None, None

        # Connect via WebSocket to get cookies
        import websocket
        ws_url = notion_tab.get("webSocketDebuggerUrl")

        if not ws_url:
            print("❌ Could not get WebSocket URL")
            return None, None

        ws = websocket.create_connection(ws_url)

        # Enable Network domain
        ws.send(json.dumps({"id": 1, "method": "Network.enable"}))
        ws.recv()

        # Get all cookies
        ws.send(json.dumps({"id": 2, "method": "Network.getAllCookies"}))
        response = json.loads(ws.recv())

        ws.close()

        cookies = response.get("result", {}).get("cookies", [])

        # Filter Notion cookies
        notion_cookies = [c for c in cookies if "notion.so" in c.get("domain", "")]

        if not notion_cookies:
            print("❌ No Notion cookies found. Please make sure you're logged in.")
            return None, None

        # Format as cookie string
        cookie_string = "; ".join([f"{c['name']}={c['value']}" for c in notion_cookies])

        # Extract user_id
        user_id = ""
        for c in notion_cookies:
            if c['name'] == 'notion_user_id':
                user_id = c['value']
                break

        return cookie_string, user_id

    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None


def save_cookies(cookie_string, user_id):
    """Save cookies to config files"""
    config_dir = Path.home() / ".config" / "notion"
    config_dir.mkdir(parents=True, exist_ok=True)

    cookie_file = config_dir / "cookies.txt"
    user_id_file = config_dir / "user_id.txt"

    cookie_file.write_text(cookie_string)
    user_id_file.write_text(user_id)

    print("\n" + "=" * 80)
    print("✅ Cookies saved successfully!")
    print(f"   📁 Cookie file: {cookie_file}")
    print(f"   📁 User ID file: {user_id_file}")
    print(f"   👤 User ID: {user_id}")
    print(f"   🍪 Cookies: {len(cookie_string)} characters")
    print("=" * 80)


def main():
    # Install websocket-client if needed
    try:
        import websocket
    except ImportError:
        print("📦 Installing websocket-client...")
        subprocess.run([
            sys.executable, "-m", "pip", "install",
            "--break-system-packages", "websocket-client"
        ], capture_output=True)
        import websocket

    cookie_string, user_id = get_chrome_cookies()

    if cookie_string:
        save_cookies(cookie_string, user_id)
        print("\n✨ Ready to upload images and submit template!")
        return 0
    else:
        return 1


if __name__ == "__main__":
    exit(main())
