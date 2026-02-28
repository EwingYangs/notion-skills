#!/usr/bin/env python3
"""
Interactive script to save Notion cookies
"""
from pathlib import Path
import sys


def save_cookies():
    print("=" * 80)
    print("Notion Cookie Setup")
    print("=" * 80)
    print("\nPlease follow these steps:")
    print("1. Open your browser and go to: https://www.notion.so/profile/templates")
    print("2. Open DevTools (F12 or Cmd+Option+I)")
    print("3. Go to the 'Network' tab")
    print("4. Refresh the page")
    print("5. Click on any request to 'notion.so'")
    print("6. Find the 'Cookie' header in the request headers")
    print("7. Copy the entire cookie value")
    print("\n" + "=" * 80)

    cookies = input("\nPaste the Cookie header value here: ").strip()

    if not cookies:
        print("Error: No cookies provided")
        sys.exit(1)

    # Extract user_id from cookies
    user_id = ""
    for cookie in cookies.split(';'):
        cookie = cookie.strip()
        if cookie.startswith('notion_user_id='):
            user_id = cookie.split('=', 1)[1]
            break

    if not user_id:
        print("\nWarning: Could not find notion_user_id in cookies")
        user_id = input("Please enter your notion_user_id manually: ").strip()

    # Save to files
    config_dir = Path.home() / ".config" / "notion"
    config_dir.mkdir(parents=True, exist_ok=True)

    cookie_file = config_dir / "cookies.txt"
    user_id_file = config_dir / "user_id.txt"

    cookie_file.write_text(cookies)
    user_id_file.write_text(user_id)

    print("\n" + "=" * 80)
    print("✅ Cookies saved successfully!")
    print(f"   Cookie file: {cookie_file}")
    print(f"   User ID file: {user_id_file}")
    print(f"   User ID: {user_id}")
    print("=" * 80)


if __name__ == "__main__":
    save_cookies()
