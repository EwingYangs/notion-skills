---
name: notion-market-publish-skill
description: Publish Notion templates to the Notion template marketplace. Automates the complete workflow with AI-powered metadata generation and script-based execution. Use when user wants to publish a Notion template, mentions "notion template marketplace", "publish notion template", or provides a Notion template URL with images for publishing.
---

# Notion Market Publish Skill

## Overview

Automate publishing Notion templates to the official Notion template marketplace. This skill uses AI to generate intelligent metadata (locale detection, slug generation, category selection, descriptions) and scripts to execute concrete operations (API calls, image uploads, submission).

## Prerequisites

1. Python 3.7+ with `requests` library:
   ```bash
   pip install -r requirements.txt
   ```
2. Notion API key stored at `~/.config/notion/api_key`
3. (Optional) Stripe account for paid templates

## Workflow

### Step 1: Gather User Input

Ask the user for:
1. **Template URL** (required) - e.g., `https://opaque-bag-aa9.notion.site/3148eab86c0980cdaf39fc5cdeb3bcfb`
2. **Image directory** (required) - e.g., `~/Documents/clipno/clipno-template/繁体/`
3. **Price in JPY** (optional) - For paid templates
4. **Stripe product ID** (optional) - For paid templates

### Step 2: Get Template Content

Use the script to fetch the template title and page content from Notion API:

```bash
python scripts/notion_api.py get-content <template_url>
```

This returns JSON with the title, sub-page names, headings, and paragraphs:

```json
{
  "title": "知識庫管理系統",
  "subpages": ["📥 收件匣", "🗂️ 資料庫", "📝 每日筆記"],
  "headings": [
    {"level": 2, "text": "功能特色"},
    {"level": 2, "text": "使用方式"}
  ],
  "paragraphs": ["這是一個全功能的知識管理系統..."]
}
```

### Step 3: AI Analysis and Generation

**AI performs all intelligent generation** (do NOT use scripts for this):

1. **Detect Locale** - Analyze the title to determine language:
   - Korean characters (한국어) → `ko-KR`
   - Japanese characters (日本語) → `ja-JP`
   - Traditional Chinese (繁體中文) → `zh-TW`
   - Simplified Chinese (简体中文) → `zh-CN`
   - Default → `en-US`

2. **Generate Slug** - Create English slug from title:
   - Translate key terms to English
   - Convert to lowercase with hyphens
   - Add 4 random digits
   - Example: "知識庫管理系統" → "knowledge-base-management-system-1234"

3. **Select Categories** - Read `category.json` and select top 3 most relevant categories:
   - Analyze title, subpages, and headings for full context
   - Match with category names and descriptions
   - Return 3 `contentful_id` values

4. **Generate Emoji** - Choose appropriate emoji based on title and content:
   - 📚 for knowledge/learning
   - 📝 for notes/content
   - 🎨 for creative/design
   - 💼 for business
   - 📊 for projects/data
   - etc.

5. **Generate Descriptions** (use title + subpages + headings + paragraphs as context):
   - **shortDescription**: 1-2 sentences describing the template's core purpose, informed by actual page structure
   - **longDescription**: Detailed description listing key features/modules derived from subpage names and headings
   - Use the detected locale's language for descriptions
   - Example: if subpages are ["📥 收件匣", "🗂️ 資料庫", "📝 每日筆記"], mention these as actual features

### Step 4: Create Stripe Payment Link (If Paid)

If user provided price and Stripe product ID:

1. Use `mcp__stripe__list_prices` to check existing prices
2. Use `mcp__stripe__create_price` to create one-time JPY price
3. Use `mcp__stripe__create_payment_link` with:
   - Price ID from step 2
   - Quantity: 1
   - Success URL: template URL

Convert JPY to USD (divide by 150, round to integer) for the `price` field.

### Step 5: Get Notion Cookies (Automated)

Run the browser automation script to get cookies:

```bash
node scripts/get_cookies.js
```

This script will:
1. Launch Chrome browser (visible, not headless)
2. Navigate to `https://www.notion.so/profile/templates`
3. Wait for user to login if needed (5 seconds)
4. Extract all cookies and user_id
5. Save to `~/.config/notion/cookies.txt` and `~/.config/notion/user_id.txt`

The cookies will be automatically used by subsequent commands.

**Note**: If you don't have Node.js/puppeteer, you can manually:
1. Open browser → `https://www.notion.so/profile/templates`
2. Open DevTools (F12) → Network tab
3. Copy full `Cookie` header and save to `~/.config/notion/cookies.txt`
4. Copy `notion_user_id` value and save to `~/.config/notion/user_id.txt`

### Step 6: Upload Images

Run the script to upload all images (cookies auto-loaded):

```bash
python scripts/notion_api.py upload-images <image_dir>
```

The script finds and uploads:
- Desktop cover: `desktop.*`, `cover.*`, `image.*` → `image` (1920x1200)
- Mobile cover: `mobile_image.*` → `mobileImage` (600x1200)
- PC screenshots: `pc1.jpg`, `pc2.jpg`, etc. → `screenshots[]` (2048x1280)
- Mobile screenshots: `mobile1.*`, `mobile2.*`, etc. → `mobileScreenshots[]` (750x2668)

Returns JSON with all uploaded URLs.

### Step 7: Combine Data and Confirm

Merge all data into final submission payload:

```json
{
  "url": "<template_url>",
  "name": "<title>",
  "locale": "<ai_detected_locale>",
  "shortDescription": "<ai_generated_short_desc>",
  "longDescription": "<ai_generated_long_desc>",
  "categories": ["<ai_selected_cat1>", "<ai_selected_cat2>", "<ai_selected_cat3>"],
  "image": { "url": "...", "height": 1200, "width": 1920 },
  "mobileImage": { "url": "...", "height": 1200, "width": 600 },
  "emoji": "<ai_selected_emoji>",
  "purchaseUrl": "<stripe_payment_link>",
  "price": <usd_price>,
  "slug": "<ai_generated_slug>",
  "screenshots": [...],
  "mobileScreenshots": [...],
  "videos": [],
  "verifiedInstantDelivery": true,
  "isDefaultLocale": true,
  "status": "in_review"
}
```

**CRITICAL**: Display complete JSON to user and get confirmation before submitting.

### Step 8: Submit to Marketplace

After user confirms, submit using the script (cookies auto-loaded):

```bash
python scripts/notion_api.py submit '<data_json>'
```

Template will be submitted with status `in_review`.

## Division of Responsibilities

### AI Handles (Intelligent Generation)
- Locale detection from title
- Slug generation (translation + formatting)
- Category selection (semantic matching)
- Emoji selection (keyword matching)
- Description generation (context-aware)

### Scripts Handle (Concrete Operations)
- Fetching title from Notion API
- Uploading images to S3
- Submitting data to marketplace API

## Image Naming Conventions

Organize images in directory as:
- `image.jpg` or `desktop.jpg` - Desktop cover
- `mobile_image.jpg` or `mobile_image.PNG` - Mobile cover
- `pc1.jpg`, `pc2.jpg`, `pc3.jpg`, `pc4.jpg` - PC screenshots
- `mobile1.PNG`, `mobile2.PNG`, etc. - Mobile screenshots

## Supported Locales

- `en-US`: English (US)
- `ko-KR`: 한국어
- `zh-CN`: 简体中文
- `zh-TW`: 繁體中文
- `ja-JP`: 日本語
- `es-ES`: Español
- `fr-FR`: Français
- `de-DE`: Deutsch
- And more...

## Error Handling

- If Notion API key missing, instruct user to create it
- If image upload fails, verify cookies are fresh
- If submission fails, check all required fields present
- Always confirm data with user before submission

## Resources

- `scripts/notion_api.py` - Unified script for all API operations
- `requirements.txt` - Python dependencies
- `references/workflow.md` - Detailed workflow documentation
