# Nomic Embed Text Service

OpenAI-compatible embedding service using the nomic-embed-text model.

## Features

- OpenAI-compatible `/v1/embeddings` API
- Local model loading (no network required after initial download)
- Support for batch embeddings
- Configurable via environment variables
- Integration with DeepWiki RAG system

## Quick Start

### 1. Install Dependencies

```bash
# From project root
poetry install -C api
```

### 2. Download Model

模型需要下载两个部分：

#### 2.1 下载 nomic-embed-text 主模型

```bash
cd api/embedding_service

# 使用镜像源下载（国内加速）
export HF_ENDPOINT=https://hf-mirror.com

python3 -c "
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id='nomic-ai/nomic-embed-text-v1.5',
    local_dir='./models/nomic-embed-text',
    resume_download=True
)
"
```

#### 2.2 下载 nomic-bert-2048 依赖文件

模型需要 `nomic-bert-2048` 的自定义代码文件：

```bash
cd api/embedding_service/models/nomic-embed-text

# 下载配置文件
curl -sL 'https://hf-mirror.com/nomic-ai/nomic-bert-2048/resolve/main/configuration_hf_nomic_bert.py' -o configuration_hf_nomic_bert.py

# 下载模型代码文件（约2500行）
curl -sL 'https://hf-mirror.com/nomic-ai/nomic-bert-2048/resolve/main/modeling_hf_nomic_bert.py' -o modeling_hf_nomic_bert.py
```

#### 2.3 修改 config.json 使用本地路径

将 `config.json` 中的 `auto_map` 修改为本地引用：

```json
{
  "auto_map": {
    "AutoConfig": "configuration_hf_nomic_bert.NomicBertConfig",
    "AutoModel": "modeling_hf_nomic_bert.NomicBertModel"
  }
}
```

**重要**: 删除原始的 `nomic-ai/nomic-bert-2048--` 前缀，改为直接引用本地文件。

#### 2.4 验证模型文件

完整模型目录结构：

```
api/embedding_service/models/nomic-embed-text/
├── config.json                           # 需要修改 auto_map
├── config_sentence_transformers.json
├── model.safetensors                     # ~550MB
├── tokenizer.json
├── tokenizer_config.json
├── special_tokens_map.json
├── modules.json
├── vocab.txt
├── configuration_hf_nomic_bert.py        # 从 nomic-bert-2048 下载
└── modeling_hf_nomic_bert.py             # 从 nomic-bert-2048 下载（约2500行）
```

### 3. Start the Service

```bash
# Option 1: Using the startup script
./scripts/start_embedding_service.sh

# Option 2: Direct Python
python -m api.embedding_service.server

# Option 3: With custom configuration
EMBEDDING_PORT=8003 EMBEDDING_DEVICE=mps python -m api.embedding_service.server
```

### 4. Test the Service

```bash
# Health check
curl http://localhost:8002/health

# Create embedding
curl -X POST http://localhost:8002/v1/embeddings \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dummy-key" \
  -d '{"input": "Hello world", "model": "nomic-embed-text"}'
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `EMBEDDING_MODEL_NAME` | `nomic-ai/nomic-embed-text-v1.5` | Hugging Face model name |
| `EMBEDDING_CACHE_DIR` | `./models` | Model cache directory |
| `EMBEDDING_DEVICE` | `cpu` | Device (cpu, cuda, mps) |
| `EMBEDDING_HOST` | `0.0.0.0` | Server host |
| `EMBEDDING_PORT` | `8002` | Server port |
| `EMBEDDING_API_KEY` | `dummy-key` | API key for authentication |
| `EMBEDDING_MAX_BATCH_SIZE` | `32` | Maximum batch size |

### Using with DeepWiki

1. 修改 `.env` 文件：`DEEPWIKI_EMBEDDER_TYPE=openai`
2. 复制配置: `cp api/config/embedder.nomic.json api/config/embedder.json`
3. 启动 embedding 服务
4. 启动 DeepWiki 后端

## API Reference

### POST /v1/embeddings

Create embeddings for input text(s).

**Request Body:**
```json
{
  "input": "text or array of texts",
  "model": "nomic-embed-text",
  "encoding_format": "float"
}
```

**Response:**
```json
{
  "object": "list",
  "data": [
    {
      "object": "embedding",
      "embedding": [0.1, 0.2, ...],
      "index": 0
    }
  ],
  "model": "nomic-ai/nomic-embed-text-v1.5",
  "usage": {
    "prompt_tokens": 10,
    "total_tokens": 10
  }
}
```

### GET /v1/models

List available models.

### GET /health

Health check endpoint.

## Model Specifications

- **Model**: nomic-ai/nomic-embed-text-v1.5
- **Embedding Dimension**: 768
- **Max Sequence Length**: 8192 tokens
- **Model Size**: ~550MB

## Testing

```bash
VENV_PATH=$(poetry -C api env info --path)

# Run unit tests
$VENV_PATH/bin/python -m tests.unit.test_embedding_service

# Run integration tests
$VENV_PATH/bin/python -m tests.integration.test_nomic_integration
```

## Test Results

### Unit Tests (7/7 passed)
- Model Download: 本地模型加载成功
- Model Loading: 模型加载，维度 768，最大序列长度 8192
- Single Embedding: 单文本嵌入成功
- Batch Embedding: 批量嵌入成功
- Max Token Length: 支持最长 8192 tokens
- Code Snippet Embeddings: 代码片段嵌入，相似度合理
- Retrieval Accuracy: 检索准确率 75%

### Integration Tests (4/4 passed)
- Embedding Consistency: 多次加载嵌入一致性 1.0
- Code Similarity Semantics: 相似代码 0.85 vs 不同代码 0.54
- Batch vs Single Embedding: 批量与单条嵌入一致性 1.0
- OpenAI-compatible API Format: API 格式符合 OpenAI 规范

## Architecture

```
api/embedding_service/
├── __init__.py          # Module initialization
├── config.py            # Configuration management
├── model_manager.py     # Model loading and embedding
├── server.py            # FastAPI server
├── schemas.py           # Pydantic models
├── download.py          # Model download script (mirror source)
├── README.md            # This file
└── models/
    └── nomic-embed-text/  # Model files
```

## Troubleshooting

### 1. Connection refused errors
模型加载时会尝试连接 HuggingFace 下载依赖文件。确保网络通畅或使用镜像源：
```bash
export HF_ENDPOINT=https://hf-mirror.com
```

### 2. 'too many values to unpack' error
通常是 `config.json` 中的 `auto_map` 格式不正确。确保使用本地文件路径：
```json
"AutoConfig": "configuration_hf_nomic_bert.NomicBertConfig"
```
而不是：
```json
"AutoConfig": "nomic-ai/nomic-bert-2048--configuration_hf_nomic_bert.NomicBertConfig"
```

### 3. modeling_hf_nomic_bert.py 不完整
确保文件完整（约2500行），不完整的文件会导致语法错误。
