# AI Computer Controller

## 中文介绍 / Introduction

**AI Computer Controller** 是一个基于大语言模型（LLM）的智能计算机控制系统。它通过自然语言指令控制鼠标、键盘和文件系统，结合 OmniParser 视觉解析技术，实现自动化的桌面操作。

**AI Computer Controller** is an intelligent computer control system powered by Large Language Models (LLMs). It controls mouse, keyboard, and file systems through natural language commands, integrating with OmniParser visual parsing technology for automated desktop operations.

---

## 特性 / Features

- **鼠标控制 (Mouse Control)** - 精确移动、点击、拖拽、双击等操作
- **键盘控制 (Keyboard Control)** - 文本输入、快捷键、组合键支持
- **文件操作 (File Operations)** - 读写文件、目录遍历、文件管理
- **屏幕截图 (Screenshot)** - 实时捕获屏幕并转换为 Base64 格式
- **OmniParser 集成 (OmniParser Integration)** - 视觉元素解析与识别
- **LLM 支持 (LLM Support)** - 兼容 OpenAI API 格式的大语言模型
- **CLI 界面 (CLI Interface)** - 交互式命令行界面，简单易用
- **安全机制 (Safety Mechanism)** - 危险操作拦截与用户确认提示

---

## 安装 / Installation

1. 克隆或下载项目到本地目录

2. 安装依赖 / Install dependencies:
```bash
pip install -r requirements.txt
```

---

## 配置 / Configuration

创建 `.env` 文件并配置环境变量：

Create a `.env` file and configure environment variables:

```env
# LLM API Configuration
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
DEFAULT_MODEL=gpt-4o

# OmniParser Configuration
OMNIPARSER_URL=http://localhost:8000
```

### 环境变量说明 / Environment Variables

| 变量 / Variable | 说明 / Description | 示例 / Example |
|----------------|-------------------|----------------|
| `OPENAI_API_KEY` | LLM API 密钥 / API key | `sk-xxxxxxxxxxxx` |
| `OPENAI_BASE_URL` | API 端点 / API endpoint | `https://api.openai.com/v1` |
| `DEFAULT_MODEL` | 默认模型 / Default model | `gpt-4o` |
| `OMNIPARSER_URL` | OmniParser 服务地址 / OmniParser service URL | `http://localhost:8000` |

---

## 使用方法 / Usage

### 启动程序 / Start the application

```bash
python main.py
```

### 命令行选项 / Command Line Options

```bash
# 快速模式（跳过安全确认，仅限受信任环境使用）
# Fast mode (skip safety confirmation, only use in trusted environments)
python main.py --unsafe-fast-mode

# 直接执行提示词
# Execute a prompt directly
python main.py --prompt "打开记事本并输入Hello World"
```

---

## CLI 命令 / CLI Commands

在交互式界面中可用 / Available in interactive mode:

| 命令 / Command | 说明 / Description |
|---------------|-------------------|
| `/help` | 显示帮助信息 / Show help |
| `/history` | 查看操作历史 / View action history |
| `/log` | 查看日志 / View logs |
| `/screenshot` | 截取屏幕 / Take screenshot |
| `/status` | 显示系统状态 / Show system status |
| `/quit` | 退出程序 / Quit application |

---

## 示例工作流 / Example Workflow

1. 启动程序 / Start the application:
```bash
python main.py
```

2. 输入自然语言指令 / Enter natural language command:
```
> 打开记事本并输入"Hello World"
> Open Notepad and type "Hello World"
```

3. AI 将自动解析并执行操作 / AI parses and executes the action automatically

4. 查看执行结果 / View execution result

---

## ⚠️ 安全警告 / Safety Warning

**重要提示:** 本程序可以控制您的计算机执行各种操作。请谨慎使用！

**IMPORTANT:** This program can control your computer and perform various operations. Use with caution!

- **始终在使用前备份重要数据** / **Always backup important data before use**
- **在受信任的环境中运行** / **Run in trusted environments only**
- **`--unsafe-fast-mode` 将跳过安全确认** / **`--unsafe-fast-mode` will skip safety confirmation**
- **危险操作（如删除文件、执行脚本）将被拦截或需要确认** / **Dangerous actions (like deleting files, executing scripts) will be blocked or require confirmation**

---

## License

MIT
