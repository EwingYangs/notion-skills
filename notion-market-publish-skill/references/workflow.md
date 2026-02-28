# Notion Template Publishing Workflow

## Overview

This document describes the complete workflow for publishing a Notion template to the marketplace.

## Prerequisites

1. Notion API key stored at `~/.config/notion/api_key`
2. Template URL (e.g., `https://opaque-bag-aa9.notion.site/3148eab86c0980cdaf39fc5cdeb3bcfb`)
3. Image directory with template screenshots
4. (Optional) Price in JPY and Stripe product ID for paid templates

## Workflow Steps

### 1. Extract Template Information

Use `publish_template.py` to extract and generate template metadata:

```bash
python scripts/publish_template.py <template_url> <image_dir> [price_jpy] [stripe_product_id]
```

This script:
- Extracts page ID from URL
- Fetches page title and child pages via Notion API
- Detects locale from title
- Generates slug (title + 4 random digits)
- Selects top 3 categories from category.json
- Generates appropriate emoji
- Creates short and long descriptions

### 2. Create Stripe Payment Link (Optional)

If the template is paid, create a Stripe payment link:

1. Find or create the Stripe product
2. Create a price in JPY (one-time payment)
3. Create a payment link with success URL pointing to the template
4. Add `purchaseUrl` and `price` (in USD) to the template data

Use Stripe MCP tools:
- `mcp__stripe__list_products` - Find product
- `mcp__stripe__create_price` - Create price
- `mcp__stripe__create_payment_link` - Create payment link

### 3. Get Notion Cookies

Open browser and navigate to `https://www.notion.so/profile/templates` to get cookies.

Extract the full cookie string from browser DevTools (Network tab).

### 4. Upload Images

Use `upload_images.py` to upload all images:

```bash
python scripts/upload_images.py <image_dir> "<cookies>" <user_id>
```

Image naming conventions:
- Desktop cover: `desktop.*`, `cover.*`, or `image.*`
- Mobile cover: `mobile.*` or `phone.*`
- PC screenshots: numbered files (e.g., `1.jpg`, `2.jpg`)
- Mobile screenshots: files with "mobile" or "phone" in name

The script returns URLs for:
- `image` - Desktop cover (1920x1200)
- `mobileImage` - Mobile cover (600x1200)
- `screenshots` - Up to 4 PC screenshots (2048x1280)
- `mobileScreenshots` - Up to 4 mobile screenshots (750x2668)

### 5. Combine Data

Merge the template metadata from step 1 with image URLs from step 4.

Add payment information from step 2 if applicable.

### 6. Submit Template

Use `submit_template.py` to submit the final data:

```bash
python scripts/submit_template.py '<data_json>' "<cookies>" <user_id>
```

The template will be submitted with status `in_review`.

## Data Structure

Complete template submission data:

```json
{
  "url": "https://...",
  "name": "Template Name",
  "locale": "en-US",
  "shortDescription": "Brief description...",
  "longDescription": "Detailed description...",
  "categories": ["cat1", "cat2", "cat3"],
  "image": {
    "url": "https://...",
    "height": 1200,
    "width": 1920
  },
  "mobileImage": {
    "url": "https://...",
    "height": 1200,
    "width": 600
  },
  "emoji": "📝",
  "purchaseUrl": "https://buy.stripe.com/...",
  "price": 14,
  "slug": "template-name-1234",
  "screenshots": [...],
  "mobileScreenshots": [...],
  "videos": [],
  "verifiedInstantDelivery": true,
  "isDefaultLocale": true,
  "status": "in_review"
}
```

## Supported Locales

- `en-US`: English (US)
- `de-DE`: Deutsch
- `ko-KR`: 한국어
- `zh-CN`: 简体中文
- `zh-TW`: 繁體中文
- `ja-JP`: 日本語
- `es-ES`: Español (España)
- `es-LA`: Español (Latinoamérica)
- `pt-BR`: Português (Brasil)
- `fr-FR`: Français (France)
- `da-DK`: Dansk
- `fi-FI`: Suomi
- `nb-NO`: Norsk
- `nl-NL`: Nederlands
- `sv-SE`: Svenska
- `en-GB`: English (UK)
- `th-TH`: ภาษาไทย
- `id-ID`: Bahasa Indonesia
- `vi-VN`: Tiếng Việt
- `he-IL`: עברית
- `ar-SA`: العربية

## Error Handling

- If Notion API key is not found, the script will fail with a clear error message
- If image upload fails, check cookies and user_id
- If template submission fails, verify all required fields are present
- Always confirm data with user before final submission
