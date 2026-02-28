#!/usr/bin/env python3
"""
Upload images to Notion and submit template to marketplace
This script only does concrete operations - no AI/generation logic
"""
import sys
import requests
from pathlib import Path
from typing import Dict, Any, List
import json


def get_notion_api_key() -> str:
    """Get Notion API key from config file"""
    api_key_path = Path.home() / ".config" / "notion" / "api_key"
    if not api_key_path.exists():
        raise FileNotFoundError(f"Notion API key not found at {api_key_path}")
    return api_key_path.read_text().strip()


def get_cookies() -> str:
    """Get Notion cookies from saved file"""
    cookie_file = Path.home() / ".config" / "notion" / "cookies.txt"
    if not cookie_file.exists():
        raise FileNotFoundError(
            f"Cookies not found at {cookie_file}\n"
            "Run: node scripts/get_cookies.js to get cookies from browser"
        )
    return cookie_file.read_text().strip()


def get_user_id() -> str:
    """Get Notion user_id from saved file"""
    user_id_file = Path.home() / ".config" / "notion" / "user_id.txt"
    if not user_id_file.exists():
        raise FileNotFoundError(
            f"User ID not found at {user_id_file}\n"
            "Run: node scripts/get_cookies.js to get user ID from browser"
        )
    return user_id_file.read_text().strip()


def extract_page_id(url: str) -> str:
    """Extract page ID from Notion URL"""
    # Strip query string and fragment before parsing
    url = url.split('?')[0].split('#')[0]
    parts = url.rstrip('/').split('/')
    page_id = parts[-1].split('-')[-1] if '-' in parts[-1] else parts[-1]
    if len(page_id) == 32:
        return f"{page_id[:8]}-{page_id[8:12]}-{page_id[12:16]}-{page_id[16:20]}-{page_id[20:]}"
    return page_id


def get_page_title(page_id: str, api_key: str) -> str:
    """Get page title from Notion API"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }

    response = requests.get(f"https://api.notion.com/v1/pages/{page_id}", headers=headers)
    response.raise_for_status()
    page_info = response.json()

    title_prop = page_info.get("properties", {}).get("title", {})
    title = title_prop.get("title", [{}])[0].get("plain_text", "Untitled")
    return title


def get_rich_text(rich_text_list: list) -> str:
    """Extract plain text from Notion rich_text array"""
    return "".join(t.get("plain_text", "") for t in rich_text_list)


def fetch_blocks(block_id: str, headers: dict) -> List[dict]:
    """Fetch child blocks of a given block_id"""
    response = requests.get(
        f"https://api.notion.com/v1/blocks/{block_id}/children",
        headers=headers,
        params={"page_size": 100}
    )
    if not response.ok:
        return []
    return response.json().get("results", [])


def extract_blocks_content(blocks: List[dict], headers: dict, depth: int,
                           subpages: list, headings: list, paragraphs: list,
                           databases: list) -> None:
    """Recursively extract meaningful content from blocks up to given depth"""
    for block in blocks:
        block_type = block.get("type")
        block_content = block.get(block_type, {})

        if block_type == "child_page":
            title = block_content.get("title", "")
            if title:
                subpages.append(title)

        elif block_type == "child_database":
            title = block_content.get("title", "")
            if title:
                databases.append(title)

        elif block_type in ("heading_1", "heading_2", "heading_3"):
            text = get_rich_text(block_content.get("rich_text", []))
            if text:
                headings.append({"level": int(block_type[-1]), "text": text})

        elif block_type in ("paragraph", "callout", "quote"):
            text = get_rich_text(block_content.get("rich_text", []))
            if text and len(paragraphs) < 8:
                paragraphs.append(text)

        elif block_type in ("bulleted_list_item", "numbered_list_item", "to_do"):
            text = get_rich_text(block_content.get("rich_text", []))
            if text and len(paragraphs) < 8:
                paragraphs.append(text)

        # Recurse into container blocks
        if depth > 0 and block.get("has_children"):
            if block_type in ("column_list", "column", "toggle", "callout",
                              "bulleted_list_item", "numbered_list_item", "quote",
                              "synced_block", "template"):
                children = fetch_blocks(block.get("id"), headers)
                extract_blocks_content(children, headers, depth - 1,
                                       subpages, headings, paragraphs, databases)


def get_page_content(page_id: str, api_key: str) -> Dict[str, Any]:
    """Get page title and child block content from Notion API for AI description generation"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }

    # Fetch page title
    response = requests.get(f"https://api.notion.com/v1/pages/{page_id}", headers=headers)
    response.raise_for_status()
    page_info = response.json()
    title_prop = page_info.get("properties", {}).get("title", {})
    title = title_prop.get("title", [{}])[0].get("plain_text", "Untitled")

    # Fetch child blocks (first level)
    top_blocks = fetch_blocks(page_id, headers)

    subpages = []
    headings = []
    paragraphs = []
    databases = []

    # Recursively extract content up to 3 levels deep
    extract_blocks_content(top_blocks, headers, depth=3,
                           subpages=subpages, headings=headings,
                           paragraphs=paragraphs, databases=databases)

    return {
        "title": title,
        "subpages": subpages,
        "databases": databases,
        "headings": headings,
        "paragraphs": paragraphs
    }


def upload_image(image_path: Path, cookies: str, user_id: str) -> Dict[str, Any]:
    """Upload a single image to Notion S3"""
    file_size = image_path.stat().st_size
    content_type = "image/jpeg" if image_path.suffix.lower() in ['.jpg', '.jpeg'] else "image/png"

    headers = {
        "accept": "*/*",
        "content-type": "application/json",
        "cookie": cookies,
        "notion-audit-log-platform": "web",
        "notion-client-version": "23.13.20260227.0159",
        "origin": "https://www.notion.so",
        "referer": "https://www.notion.so/profile/templates/form/new",
        "x-notion-active-user-header": user_id,
    }

    # Get upload URL
    payload = {
        "bucket": "public",
        "name": image_path.name,
        "contentType": content_type,
        "supportExtraHeaders": True,
        "contentLength": file_size
    }

    response = requests.post(
        "https://www.notion.so/api/v3/getUploadFileUrl",
        headers=headers,
        json=payload
    )
    response.raise_for_status()
    upload_data = response.json()

    # Upload to S3
    upload_type = upload_data.get("type", "PUT")

    if upload_type == "POST":
        # Use POST with multipart form data
        post_url = upload_data.get("signedUploadPostUrl")
        fields = upload_data.get("fields", {})

        with open(image_path, 'rb') as f:
            files = {'file': (image_path.name, f, content_type)}
            s3_response = requests.post(post_url, data=fields, files=files)
            s3_response.raise_for_status()
    else:
        # Use PUT (legacy)
        upload_url = upload_data.get("signedPutUrl")
        with open(image_path, 'rb') as f:
            s3_response = requests.put(upload_url, data=f, headers={"Content-Type": content_type})
            s3_response.raise_for_status()

    return {
        "url": upload_data.get("url"),
        "width": 1920 if "desktop" in image_path.name.lower() or "pc" in image_path.name.lower() or "image" in image_path.name.lower() else 750,
        "height": 1200 if "desktop" in image_path.name.lower() or "pc" in image_path.name.lower() or "image" in image_path.name.lower() else 2668
    }


def find_images(image_dir: Path) -> Dict[str, Any]:
    """Find desktop, mobile, and screenshot images"""
    images = {
        "desktop": None,
        "mobile": None,
        "screenshots": [],
        "mobile_screenshots": []
    }

    all_files = sorted([f for f in image_dir.glob("*") if f.is_file() and f.suffix.lower() in ['.jpg', '.jpeg', '.png']])

    # Find desktop image
    for f in all_files:
        if any(x in f.name.lower() for x in ["desktop", "cover", "image"]) and "mobile" not in f.name.lower():
            images["desktop"] = f
            break

    # Find mobile cover
    for f in all_files:
        if "mobile" in f.name.lower() and "image" in f.name.lower():
            images["mobile"] = f
            break

    # Find PC screenshots (numbered)
    for f in all_files:
        if "pc" in f.name.lower() and f != images["desktop"]:
            images["screenshots"].append(f)

    # Find mobile screenshots (numbered)
    for f in all_files:
        if "mobile" in f.name.lower() and f != images["mobile"] and any(c.isdigit() for c in f.name):
            images["mobile_screenshots"].append(f)

    images["screenshots"] = images["screenshots"][:4]
    images["mobile_screenshots"] = images["mobile_screenshots"][:4]

    return images


def submit_template(data: dict, cookies: str, user_id: str) -> dict:
    """Submit template draft to Notion marketplace"""
    headers = {
        "accept": "*/*",
        "accept-language": "zh-CN,zh;q=0.9",
        "content-type": "application/json",
        "cookie": cookies,
        "notion-audit-log-platform": "web",
        "notion-client-version": "23.13.20260129.2129",
        "origin": "https://www.notion.so",
        "referer": "https://www.notion.so/profile/templates/form/new",
        "x-notion-active-user-header": user_id,
    }

    response = requests.post(
        "https://www.notion.so/api/v3/submitTemplateDraft",
        headers=headers,
        json=data
    )
    response.raise_for_status()
    return response.json()


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Get title: python script.py get-title <template_url>")
        print("  Get content: python script.py get-content <template_url>")
        print("  Upload images: python script.py upload-images <image_dir> [cookies] [user_id]")
        print("  Submit: python script.py submit '<data_json>' [cookies] [user_id]")
        print("\nNote: If cookies and user_id are not provided, they will be read from ~/.config/notion/")
        sys.exit(1)

    command = sys.argv[1]

    if command == "get-title":
        if len(sys.argv) < 3:
            print("Usage: python script.py get-title <template_url>")
            sys.exit(1)

        template_url = sys.argv[2]
        api_key = get_notion_api_key()
        page_id = extract_page_id(template_url)
        title = get_page_title(page_id, api_key)
        print(json.dumps({"title": title}, ensure_ascii=False))

    elif command == "get-content":
        if len(sys.argv) < 3:
            print("Usage: python script.py get-content <template_url>")
            sys.exit(1)

        template_url = sys.argv[2]
        api_key = get_notion_api_key()
        page_id = extract_page_id(template_url)
        content = get_page_content(page_id, api_key)
        print(json.dumps(content, ensure_ascii=False, indent=2))

    elif command == "upload-images":
        if len(sys.argv) < 3:
            print("Usage: python script.py upload-images <image_dir> [cookies] [user_id]")
            sys.exit(1)

        image_dir = Path(sys.argv[2]).expanduser()

        # Get cookies and user_id from args or saved files
        if len(sys.argv) >= 5:
            cookies = sys.argv[3]
            user_id = sys.argv[4]
        else:
            print("Reading cookies from ~/.config/notion/...", file=sys.stderr)
            cookies = get_cookies()
            user_id = get_user_id()

        if not image_dir.exists():
            print(f"Error: Image directory not found: {image_dir}")
            sys.exit(1)

        images = find_images(image_dir)
        result = {}

        if images["desktop"]:
            print(f"Uploading desktop image: {images['desktop'].name}", file=sys.stderr)
            result["image"] = upload_image(images["desktop"], cookies, user_id)

        if images["mobile"]:
            print(f"Uploading mobile image: {images['mobile'].name}", file=sys.stderr)
            result["mobileImage"] = upload_image(images["mobile"], cookies, user_id)

        if images["screenshots"]:
            result["screenshots"] = []
            for screenshot in images["screenshots"]:
                print(f"Uploading screenshot: {screenshot.name}", file=sys.stderr)
                result["screenshots"].append(upload_image(screenshot, cookies, user_id))

        if images["mobile_screenshots"]:
            result["mobileScreenshots"] = []
            for screenshot in images["mobile_screenshots"]:
                print(f"Uploading mobile screenshot: {screenshot.name}", file=sys.stderr)
                result["mobileScreenshots"].append(upload_image(screenshot, cookies, user_id))

        print(json.dumps(result, indent=2))

    elif command == "submit":
        if len(sys.argv) < 3:
            print("Usage: python script.py submit '<data_json>' [cookies] [user_id]")
            sys.exit(1)

        data_json = sys.argv[2]

        # Get cookies and user_id from args or saved files
        if len(sys.argv) >= 5:
            cookies = sys.argv[3]
            user_id = sys.argv[4]
        else:
            print("Reading cookies from ~/.config/notion/...", file=sys.stderr)
            cookies = get_cookies()
            user_id = get_user_id()

        data = json.loads(data_json)
        result = submit_template(data, cookies, user_id)
        print(json.dumps(result, indent=2))

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
