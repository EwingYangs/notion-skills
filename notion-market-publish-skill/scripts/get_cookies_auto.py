#!/usr/bin/env python3
"""
Automatically get Notion cookies using Playwright
Opens browser, navigates to Notion, and extracts cookies
"""
from playwright.sync_api import sync_playwright
from pathlib import Path
import json
import time


def get_cookies_with_playwright():
    """Open browser and get Notion cookies"""
    print("🌐 Opening browser to get Notion cookies...")

    with sync_playwright() as p:
        # Launch browser (visible so user can login if needed)
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        print("📄 Navigating to Notion templates page...")
        try:
            page.goto("https://www.notion.so/profile/templates", timeout=60000)
        except:
            print("⚠️  Page load timeout, but continuing...")

        print("\n" + "=" * 80)
        print("👤 Please login to Notion in the browser window")
        print("⏳ Waiting for you to login...")
        print("   Script will automatically detect when you're logged in")
        print("=" * 80 + "\n")

        # Wait and check for login
        max_wait = 120  # Maximum 2 minutes
        waited = 0
        check_interval = 5

        while waited < max_wait:
            time.sleep(check_interval)
            waited += check_interval

            cookies = context.cookies()
            notion_cookies = [c for c in cookies if "notion.so" in c.get("domain", "")]

            # Check if we have token_v2 (means logged in)
            has_token = any(c['name'] == 'token_v2' for c in notion_cookies)
            has_user_id = any(c['name'] == 'notion_user_id' for c in notion_cookies)

            if has_token and has_user_id:
                print(f"✅ Login detected! (waited {waited} seconds)")
                break

            if waited % 15 == 0:
                print(f"⏳ Still waiting... ({waited}/{max_wait} seconds)")

        # Get final cookies
        cookies = context.cookies()
        notion_cookies = [c for c in cookies if "notion.so" in c.get("domain", "")]

        if not notion_cookies:
            print("❌ No Notion cookies found. Please make sure you're logged in.")
            print("   Waiting another 10 seconds...")
            time.sleep(10)
            cookies = context.cookies()
            notion_cookies = [c for c in cookies if "notion.so" in c.get("domain", "")]

        if not notion_cookies:
            print("❌ Still no cookies found. Please try again and make sure to login.")
            browser.close()
            return None, None

        # Format as cookie string
        cookie_string = "; ".join([f"{c['name']}={c['value']}" for c in notion_cookies])

        # Extract user_id
        user_id = ""
        for c in notion_cookies:
            if c['name'] == 'notion_user_id':
                user_id = c['value']
                break

        if not user_id:
            print("⚠️  Warning: notion_user_id not found in cookies")

        browser.close()

        return cookie_string, user_id


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
    try:
        cookie_string, user_id = get_cookies_with_playwright()

        if cookie_string:
            save_cookies(cookie_string, user_id)
            print("\n✨ Ready to upload images and submit template!")
        else:
            print("\n❌ Failed to get cookies. Please try again.")
            return 1

        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
