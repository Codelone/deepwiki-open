import os
# 上面所有环境变量在这里也写死，避免终端问题
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
os.environ["HF_HUB_DOWNLOAD_URL"] = "https://hf-mirror.com"
os.environ["HF_HOME"] = os.path.expanduser("~/.hf_cache")
os.environ["HF_HUB_DOWNLOAD_TIMEOUT"] = "600"

from huggingface_hub import snapshot_download

snapshot_download(
    repo_id="nomic-ai/nomic-embed-text-v1.5",
    local_dir="./models/nomic-embed-text",
    resume_download=True,
    force_download=False
)