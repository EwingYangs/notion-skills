# notion-skills

English | [中文](README.zh.md)

Skills for Claude Code / Cursor / OpenClaw. Clip web pages to Notion and more.

## Prerequisites

* Node.js (v18+)
* Chrome or Chromium browser
* Ability to run `npx tsx` commands

## Installation

### Quick Install (if supported)

```bash
npx skills add EwingYangs/notion-skills
```

### Register as Plugin Marketplace

Run in Claude Code:

```
/plugin marketplace add EwingYangs/notion-skills
```

### Install Skills

**Option 1: Via Browse UI**

1. Select **Browse and install plugins**
2. Select **notion-skills**
3. Select the skill(s) to install
4. Select **Install now**

**Option 2: Direct Install**

```bash
# Install specific plugin (after adding marketplace)
/plugin install notion-clipper-skill@notion-skills
```

**Option 3: Direct Clone**

```bash
git clone https://github.com/EwingYangs/notion-skills.git
cd notion-skills/notion-clipper-skill/scripts && npm install
```

**Option 4: Ask the Agent**

Simply tell Claude Code:

> Please install Skills from github.com/EwingYangs/notion-skills

## Update Skills

To update to the latest version:

1. Run `/plugin` in Claude Code
2. Switch to **Marketplaces** tab
3. Select **notion-skills**
4. Choose **Update marketplace**

## Available Skills

### notion-clipper-skill

Clip web pages to Notion. Uses Chrome CDP for full JavaScript rendering, converts to Markdown, then to Notion blocks.

> 💡 Want a better clipping experience? Try [Clipno](https://clipno.app) — a dedicated web clipper with broader site support and richer formatting.

**First run**: Dependencies are auto-installed when you run the script. No manual setup needed.

#### Prerequisites

1. **Notion API Key**: Create integration at https://notion.so/my-integrations
2. **Store the key**:
```bash
mkdir -p ~/.config/notion
echo "ntn_your_key_here" > ~/.config/notion/api_key
```
3. **Share database/page** with your integration (click "..." → "Connect to" → your integration)

#### Usage

Replace `${SKILL_DIR}` with the path to `notion-clipper-skill` (e.g. `notion-skills/notion-clipper-skill`).

```bash
# Clip to database by name (recommended)
npx -y tsx ${SKILL_DIR}/scripts/main.ts <url> --database-name "Resource"

# Clip to database by ID
npx -y tsx ${SKILL_DIR}/scripts/main.ts <url> --database <database_id>

# Append to existing page
npx -y tsx ${SKILL_DIR}/scripts/main.ts <url> --page <page_id>

# List accessible databases
npx -y tsx ${SKILL_DIR}/scripts/main.ts --list-databases

# Wait mode (for login-required pages)
npx -y tsx ${SKILL_DIR}/scripts/main.ts <url> -n "Resource" --wait
```

#### Options

| Option | Description |
|--------|-------------|
| `<url>` | URL to clip |
| `--database-name, -n <name>` | Target database by name (searches for match) |
| `--database, -d <id>` | Target database by ID |
| `--page, -p <id>` | Append to page by ID |
| `--list-databases, -l` | List databases and exit |
| `--wait, -w` | Wait for user signal before capturing |
| `--timeout, -t <ms>` | Page load timeout (default: 30000) |
| `--no-bookmark` | Omit bookmark block at top |

#### Capture Modes

| Mode | Behavior | Use When |
|------|----------|----------|
| Auto (default) | Capture when network idle | Public pages |
| Wait (`--wait`) | User presses Enter when ready | Login-required, paywalls |

#### Examples

```bash
# Clip tweet to "Resource" database
npx -y tsx ${SKILL_DIR}/scripts/main.ts "https://x.com/user/status/123" -n "Resource"

# Clip article requiring login
npx -y tsx ${SKILL_DIR}/scripts/main.ts "https://medium.com/article" -n "Reading" --wait

# Append to page
npx -y tsx ${SKILL_DIR}/scripts/main.ts "https://example.com/post" -p xyz789
```

#### Database Setup

Create a Notion database with:
- **Name** (Title) - Page title
- **URL** (URL) - Source URL (optional; auto-detected from schema)

#### Troubleshooting

| Issue | Solution |
|-------|----------|
| Script fails (missing deps) | Run `cd <skill_path>/notion-clipper-skill/scripts && npm install` |
| Chrome not found | Set `NOTION_CLIPPER_CHROME_PATH` |
| ECONNREFUSED / empty body | Run `unset https_proxy http_proxy all_proxy` first, or use terminal without proxy |
| Content missing | Use `--wait` for dynamic/lazy-loaded pages |
| Notion API error | Ensure integration has access to database |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `NOTION_CLIPPER_CHROME_PATH` | Custom Chrome executable path |
| `NOTION_CLIPPER_CHROME_PROFILE_DIR` | Custom Chrome profile directory |

## License

MIT
