#!/usr/bin/env python3
"""
Helper functions to read Notion cookies from saved files
"""
from pathlib import Path
import os


def get_cookies_path() -> Path:
    """Get path to saved cookies file"""
    return Path.home() / ".config" / "notion" / "cookies.txt"


def get_user_id_path() -> Path:
    """Get path to saved user_id file"""
    return Path.home() / ".config" / "notion" / "user_id.txt"


def read_cookies() -> str:
    """Read cookies from saved file"""
    cookie_file = get_cookies_path()
    if not cookie_file.exists():
        raise FileNotFoundError(
            f"Cookies not found at {cookie_file}\n"
            "Run: node scripts/get_cookies.js"
        )
    return cookie_file.read_text().strip()


def read_user_id() -> str:
    """Read user_id from saved file"""
    user_id_file = get_user_id_path()
    if not user_id_file.exists():
        raise FileNotFoundError(
            f"User ID not found at {user_id_file}\n"
            "Run: node scripts/get_cookies.js"
        )
    return user_id_file.read_text().strip()


if __name__ == "__main__":
    try:
        cookies = read_cookies()
        user_id = read_user_id()
        print(f"Cookies: {cookies[:50]}...")
        print(f"User ID: {user_id}")
    except FileNotFoundError as e:
        print(f"Error: {e}")
