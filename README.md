# Bloom 写作助手

基于大语言模型的博客写作助手工具，提供URL slug生成和图片上传功能。

## 功能概览

- 🔗 **生成 URL Slug** - 基于文章标题智能生成 URL 友好的文件名
- 📁 **上传图片** - 上传博客图片到 Cloudflare R2 存储

## 命令使用

### 1. 生成 URL Slug (`bloom slug`)

自动为正在撰写的博客文章生成 URL slug 并重命名文件。

**功能特点：**
- 自动识别正在修改的博客文章
- 提取文章的 `title` 元信息
- 调用 LLM 生成符合 URL 规范的 slug
- 自动重命名文件为新的 slug 名称

**使用方法：**
```bash
uv run bloom slug
```

### 2. 上传博客图片 (`bloom upload`)

上传博客文章中的图片到 Cloudflare R2 存储。

**使用方法：**
```bash
# 自动识别正在修改的文章文件
uv run bloom upload

# 指定文件
uv run bloom upload path/to/article.md

# 干运行模式（不实际上传）
uv run bloom upload --dry-run

# 指定 CDN URL
uv run bloom upload --cdn-url https://your-cdn.com
```

## 智能文件检测

所有需要操作文件的命令都会自动检测正在修改的博客文件：

1. **优先级1**：工作区中修改但未提交的 `.md` 文件
2. **优先级2**：最近一次提交中的博客文件（如果只有一个）

**要求：**
- 文章必须位于 `src/content/blog/` 目录下
- 文章必须包含 YAML frontmatter 和 `title` 字段
- 同时只能有一个符合条件的文件，否则会报错

## 安装

### 开发模式安装

```bash
cd bloom
uv sync
```

### 全局命令安装

使用 `pipx` 在任何目录下都能使用 `bloom` 命令：

```bash
cd bloom
PIPX_DEFAULT_INJECT_PINNED_UV=1 pipx install --python python3.12 .
```

验证安装：
```bash
bloom --help
```

更新工具：
```bash
pipx upgrade bloom
```

卸载：
```bash
pipx uninstall bloom
```

## 环境变量

- `GOOGLE_AI_STUDIO_API_KEY`: Google AI Studio API 密钥

## 测试

单元测试：
```bash
uv run pytest
```

集成测试：
```bash
uv run python integration_test.py
```