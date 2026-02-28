# notion-skills

[English](README.md) | 中文

notion-skills 为 Claude Code / Cursor / OpenClaw 提供技能，支持将网页剪藏到 Notion 等。

## 前置要求

* Node.js（v18+）
* Chrome 或 Chromium 浏览器
* 能执行 `npx tsx` 命令

## 安装

### 快速安装（如支持）

```bash
npx skills add EwingYangs/notion-skills
```

### 注册为插件市场

在 Claude Code 中执行：

```
/plugin marketplace add EwingYangs/notion-skills
```

### 安装技能

**方式一：通过浏览界面**

1. 选择 **Browse and install plugins**
2. 选择 **notion-skills**
3. 选择要安装的技能
4. 选择 **Install now**

**方式二：直接安装**

```bash
# 添加市场后，直接安装指定插件
/plugin install notion-clipper-skill@notion-skills
```

**方式三：直接克隆**

```bash
git clone https://github.com/EwingYangs/notion-skills.git
cd notion-skills/notion-clipper-skill/scripts && npm install
```

**方式四：让 Agent 安装**

在 Claude Code 中说：

> 请从 github.com/EwingYangs/notion-skills 安装 Skills

## 更新技能

更新到最新版本：

1. 在 Claude Code 中运行 `/plugin`
2. 切换到 **Marketplaces** 标签
3. 选择 **notion-skills**
4. 选择 **Update marketplace**

## 可用技能

### notion-clipper-skill

将网页剪藏到 Notion。通过 Chrome CDP 完整渲染 JavaScript，转为 Markdown，再转为 Notion 块。

**首次运行**：执行剪藏时会自动安装依赖，无需手动操作。

#### 前置配置

1. **Notion API Key**：在 https://notion.so/my-integrations 创建集成
2. **保存密钥**：
```bash
mkdir -p ~/.config/notion
echo "ntn_your_key_here" > ~/.config/notion/api_key
```
3. **分享数据库/页面**：在 Notion 中点击「...」→「连接」→ 选择你的集成

#### 使用方式

将 `${SKILL_DIR}` 替换为 `notion-clipper-skill` 的路径（如 `notion-skills/notion-clipper-skill`）。

```bash
# 按名称剪藏到数据库（推荐）
npx -y tsx ${SKILL_DIR}/scripts/main.ts <url> --database-name "Resource"

# 按 ID 剪藏到数据库
npx -y tsx ${SKILL_DIR}/scripts/main.ts <url> --database <database_id>

# 追加到已有页面
npx -y tsx ${SKILL_DIR}/scripts/main.ts <url> --page <page_id>

# 列出可访问数据库
npx -y tsx ${SKILL_DIR}/scripts/main.ts --list-databases

# 等待模式（需登录的页面）
npx -y tsx ${SKILL_DIR}/scripts/main.ts <url> -n "Resource" --wait
```

#### 参数说明

| 参数 | 说明 |
|------|------|
| `<url>` | 要剪藏的 URL |
| `--database-name, -n <name>` | 按名称搜索目标数据库 |
| `--database, -d <id>` | 目标数据库 ID |
| `--page, -p <id>` | 追加到的页面 ID |
| `--list-databases, -l` | 列出数据库后退出 |
| `--wait, -w` | 等待用户信号后再抓取 |
| `--timeout, -t <ms>` | 页面加载超时（默认 30000） |
| `--no-bookmark` | 不添加顶部书签块 |

#### 抓取模式

| 模式 | 行为 | 适用场景 |
|------|------|----------|
| Auto（默认） | 网络空闲时抓取 | 公开页面 |
| Wait（`--wait`） | 用户按 Enter 后再抓取 | 需登录、付费墙 |

#### 示例

```bash
# 剪藏推文到 "Resource" 数据库
npx -y tsx ${SKILL_DIR}/scripts/main.ts "https://x.com/user/status/123" -n "Resource"

# 剪藏需登录的文章
npx -y tsx ${SKILL_DIR}/scripts/main.ts "https://medium.com/article" -n "Reading" --wait

# 追加到页面
npx -y tsx ${SKILL_DIR}/scripts/main.ts "https://example.com/post" -p xyz789
```

#### 数据库设置

创建 Notion 数据库时建议包含：
- **Name**（标题）- 页面标题
- **URL**（URL）- 来源链接（可选；会自动检测 schema）

#### 常见问题

| 问题 | 解决方案 |
|------|----------|
| 运行报错「找不到模块」 | 在 `scripts` 目录下执行 `npm install` |
| 找不到 Chrome | 设置 `NOTION_CLIPPER_CHROME_PATH` |
| ECONNREFUSED / 空 body | 先执行 `unset https_proxy http_proxy all_proxy`，或在未设代理的终端中运行 |
| 内容缺失 | 对动态/懒加载页面使用 `--wait` |
| Notion API 报错 | 确认集成已获得数据库访问权限 |

## 环境变量

| 变量 | 说明 |
|------|------|
| `NOTION_CLIPPER_CHROME_PATH` | 自定义 Chrome 可执行路径 |
| `NOTION_CLIPPER_CHROME_PROFILE_DIR` | 自定义 Chrome 配置目录 |

## 许可证

MIT
