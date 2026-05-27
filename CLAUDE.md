# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

DeepWiki-Open 是一个 AI 驱动的 Wiki 生成器，可为 GitHub、GitLab、Bitbucket 仓库自动生成交互式文档。项目采用前后端分离架构。

## 常用命令

### 前端 (Next.js)
```bash
# 安装依赖
yarn install

# 开发服务器 (端口 3000)
yarn dev

# 构建
yarn build

# 代码检查
yarn lint
```

### 后端 (Python FastAPI)
```bash
# 安装依赖 (需要 poetry 2.0.1)
python3 -m pip install poetry==2.0.1 && poetry install -C api

# 获取虚拟环境路径
VENV_PATH=$(poetry -C api env info --path)

# 启动 API 服务器 (端口 8001)
$VENV_PATH/bin/python -m api.main

# 或使用 poetry run (需要在项目根目录执行)
poetry run -C api python -m api.main
```

### Embedding Service (端口 8002)
```bash
# 获取虚拟环境路径
VENV_PATH=$(poetry -C api env info --path)

# 启动 embedding 服务
$VENV_PATH/bin/python -m api.embedding_service.server

# 测试服务
curl http://localhost:8002/health
curl -X POST http://localhost:8002/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{"input": "Hello world", "model": "nomic-embed-text"}'
```

### 测试
```bash
# 运行所有测试
pytest

# 运行特定目录的测试
pytest tests/unit/
pytest tests/integration/

# 运行单个测试文件
pytest tests/api/test_api.py

# 带详细输出
pytest -v
```

### Docker
```bash
# 使用 docker-compose 启动完整服务
docker-compose up
```

## 架构概览

### 前端 (src/)
- **Next.js App Router** - 使用 `src/app/` 目录结构
- **主要页面**:
  - `src/app/page.tsx` - 首页，输入仓库 URL
  - `src/app/[owner]/[repo]/page.tsx` - Wiki 展示页面
  - `src/app/wiki/projects/page.tsx` - 已处理项目列表
- **核心组件**:
  - `Ask.tsx` - RAG 问答对话组件
  - `WikiTreeView.tsx` - Wiki 目录树
  - `Mermaid.tsx` - Mermaid 图表渲染
  - `Markdown.tsx` - Markdown 内容渲染
- **API 代理**: `next.config.ts` 中配置了 rewrites，将 `/api/*` 请求代理到后端

### 后端 (api/)
- **FastAPI 应用** - `api/api.py` 定义所有 API 端点
- **入口**: `api/main.py` - 启动 uvicorn 服务器
- **核心模块**:
  - `rag.py` - RAG 检索增强生成
  - `data_pipeline.py` - 数据处理管道
  - `websocket_wiki.py` - WebSocket 实时通信
  - `simple_chat.py` - 简单对话功能
- **多模型支持**: 通过客户端模块支持不同 LLM 提供商
  - `openai_client.py` - OpenAI
  - `google_embedder_client.py` - Google AI
  - `ollama_patch.py` - Ollama 本地模型
  - `bedrock_client.py` - AWS Bedrock
  - `azureai_client.py` - Azure OpenAI
  - `openrouter_client.py` - OpenRouter
  - `dashscope_client.py` - 阿里云 DashScope
- **Embedding Service** (`api/embedding_service/`):
  - 基于 nomic-embed-text-v1.5 的本地 Embedding 服务
  - 提供 OpenAI 兼容的 `/v1/embeddings` API
  - 端口: 8002，独立于后端 API 运行
  - 详见 `api/embedding_service/README.md`

### 配置文件 (api/config/)
- `generator.json` - 文本生成模型配置
- `embedder.json` - 嵌入模型和 RAG 配置
- `repo.json` - 仓库处理规则和文件过滤

### 数据存储
数据持久化在 `~/.adalflow/` 目录:
- `repos/` - 克隆的仓库
- `databases/` - 嵌入向量和索引
- `wikicache/` - 生成的 Wiki 缓存

## 环境变量

在项目根目录创建 `.env` 文件:

```bash
# 必需 (至少一个)
GOOGLE_API_KEY=xxx        # Google Gemini 模型
OPENAI_API_KEY=xxx        # OpenAI 模型和嵌入

# 可选
OPENROUTER_API_KEY=xxx    # OpenRouter 多模型访问
DEEPWIKI_EMBEDDER_TYPE=openai  # 嵌入类型: openai | google | ollama | bedrock
OLLAMA_HOST=http://localhost:11434  # Ollama 服务地址
PORT=8001                 # API 服务器端口
SERVER_BASE_URL=http://localhost:8001  # API 服务器地址

# Embedding Service (nomic-embed-text)
EMBEDDING_PORT=8002       # Embedding 服务端口
EMBEDDING_DEVICE=cpu      # 设备: cpu | cuda | mps
```

## 关键技术栈

- **前端**: Next.js 15, React 19, TypeScript, Tailwind CSS 4
- **后端**: Python 3.11+, FastAPI, uvicorn
- **AI/ML**: adalflow, google-generativeai, openai, faiss-cpu
- **图表**: Mermaid.js
- **国际化**: next-intl (支持多语言)

### 特殊说明

**本项目属于针对内网京东cicd平台的git进行适配，开发完成后会发布到内网进行部署，因此，在开发过程中是无法连接该平台测试的，且由于前端存在跨域问题，增加了proxy接口进行git接口调用，在开发中尤其注意这一点**。

- 京东git和gitlab基本相似，只有个别接口不同
- 内网部署采用基于vllm部署的兼容openai格式的LLM模型
- 内网部署采用基于ollama部署的Embedding模型
- 本地开发推荐使用 nomic-embed-text 本地 Embedding 服务（端口 8002）

### Embedding 模型配置

当前支持的 Embedding 配置文件：

| 配置文件 | 模型 | 说明 |
|---------|------|------|
| `embedder.json` | bge-m3:567m | Ollama 默认配置 |
| `embedder.nomic.json` | nomic-embed-text-v1.5 | 本地 Embedding 服务 |
| `embedder.openai.json` | m3e-base | 外部 OpenAI 兼容 API |

使用本地 nomic-embed-text 时：
1. 启动 embedding 服务: `$VENV_PATH/bin/python -m api.embedding_service.server`
2. 设置环境变量: `DEEPWIKI_EMBEDDER_TYPE=openai`
3. 启动后端 API


## 常见问题排查

### 1. Python 命令问题
macOS 系统通常只有 `python3`，没有 `python` 命令。使用 `python3` 替代或创建别名：
```bash
alias python=python3
```

### 2. 后端依赖未找到
Poetry 会将依赖安装在独立的虚拟环境中，系统 Python 无法直接访问。必须使用虚拟环境中的 Python：
```bash
# 获取虚拟环境路径
VENV_PATH=$(poetry -C api env info --path)

# 使用虚拟环境 Python 运行
$VENV_PATH/bin/python -m api.main
```

### 3. 后端启动延迟
后端服务启动需要 5-10 秒加载模型和索引，启动后会显示 uvicorn 日志。可通过检查端口确认是否就绪：
```bash
lsof -i :8001
```

### 4. 前端代理配置
前端通过 `next.config.ts` 中的 rewrites 将 `/api/*` 请求代理到 `http://localhost:8001`，开发时无需额外配置跨域。


