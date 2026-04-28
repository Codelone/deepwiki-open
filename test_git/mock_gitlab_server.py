"""
模拟GitLab API服务器用于测试代理功能
这个服务器模拟内网GitLab环境,提供基本的API接口用于测试
"""

from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.responses import JSONResponse
import uvicorn
from typing import Optional
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(title="Mock GitLab API Server")

# 模拟的项目数据
MOCK_PROJECTS = [
    {
        "id": 1,
        "name": "test-project",
        "path": "test-project",
        "path_with_namespace": "test-group/test-project",
        "default_branch": "main",
        "description": "This is a test project",
        "web_url": "http://cicdcoding.tlb.com/test-group/test-project",
        "created_at": "2024-01-01T00:00:00.000Z",
        "last_activity_at": "2024-01-15T00:00:00.000Z"
    },
    {
        "id": 2,
        "name": "demo-repo",
        "path": "demo-repo",
        "path_with_namespace": "demo-group/demo-repo",
        "default_branch": "master",
        "description": "Demo repository for testing",
        "web_url": "http://cicdcoding.tlb.com/demo-group/demo-repo",
        "created_at": "2024-01-10T00:00:00.000Z",
        "last_activity_at": "2024-01-20T00:00:00.000Z"
    }
]

# 模拟的文件树数据
MOCK_FILE_TREE = [
    {"id": "1", "name": "README.md", "type": "blob", "path": "README.md", "mode": "100644"},
    {"id": "2", "name": "src", "type": "tree", "path": "src", "mode": "040000"},
    {"id": "3", "name": "main.py", "type": "blob", "path": "src/main.py", "mode": "100644"},
    {"id": "4", "name": "utils.py", "type": "blob", "path": "src/utils.py", "mode": "100644"},
    {"id": "5", "name": "config.json", "type": "blob", "path": "config.json", "mode": "100644"},
    {"id": "6", "name": "requirements.txt", "type": "blob", "path": "requirements.txt", "mode": "100644"},
]

# 模拟的README内容
MOCK_README = """# Test Project

This is a mock GitLab project for testing the proxy functionality.

## Features

- API proxy testing
- CORS issue resolution
- Internal CI/CD integration

## Usage

This is a test repository used for validating the DeepWiki proxy functionality.
"""


@app.get("/")
async def root():
    """根端点"""
    return {
        "message": "Mock GitLab API Server",
        "version": "v4",
        "endpoints": {
            "projects": "/api/v4/projects",
            "project_detail": "/api/v4/projects/{id}",
            "repository_tree": "/api/v4/projects/{id}/repository/tree",
            "file_raw": "/api/v4/projects/{id}/repository/files/{file_path}/raw"
        }
    }


@app.get("/api/v4/projects")
async def list_projects(
    private_token: Optional[str] = Header(None, alias="Private-Token"),
    per_page: int = Query(20, ge=1, le=100),
    page: int = Query(1, ge=1)
):
    """
    获取项目列表
    模拟GitLab的项目列表API
    """
    logger.info(f"Received request for projects list (page={page}, per_page={per_page})")
    
    # 简单的token验证(仅用于测试)
    if private_token:
        logger.info(f"Request with token: {private_token[:10]}...")
    else:
        logger.info("Request without token (public access)")
    
    # 返回所有模拟项目
    return JSONResponse(content=MOCK_PROJECTS)


@app.get("/api/v4/projects/{project_id}")
async def get_project(
    project_id: str,
    private_token: Optional[str] = Header(None, alias="Private-Token")
):
    """
    获取单个项目详情
    支持项目ID或路径编码
    """
    logger.info(f"Received request for project: {project_id}")
    
    # 尝试作为ID查找
    try:
        pid = int(project_id)
        for project in MOCK_PROJECTS:
            if project["id"] == pid:
                logger.info(f"Found project by ID: {pid}")
                return JSONResponse(content=project)
    except ValueError:
        # 不是数字,尝试作为路径查找
        # URL解码路径
        from urllib.parse import unquote
        decoded_path = unquote(project_id)
        
        for project in MOCK_PROJECTS:
            if project["path_with_namespace"] == decoded_path:
                logger.info(f"Found project by path: {decoded_path}")
                return JSONResponse(content=project)
    
    logger.error(f"Project not found: {project_id}")
    raise HTTPException(status_code=404, detail="Project not found")


@app.get("/api/v4/projects/{project_id}/repository/tree")
async def get_repository_tree(
    project_id: str,
    private_token: Optional[str] = Header(None, alias="Private-Token"),
    recursive: bool = Query(False),
    per_page: int = Query(20, ge=1, le=100),
    page: int = Query(1, ge=1),
    ref: Optional[str] = Query(None)
):
    """
    获取仓库文件树
    """
    logger.info(f"Received request for repository tree: project={project_id}, recursive={recursive}, page={page}")
    
    # 验证项目是否存在
    try:
        pid = int(project_id)
        if not any(p["id"] == pid for p in MOCK_PROJECTS):
            raise HTTPException(status_code=404, detail="Project not found")
    except ValueError:
        raise HTTPException(status_code=404, detail="Invalid project ID")
    
    # 返回模拟文件树
    # 添加分页头信息
    response = JSONResponse(content=MOCK_FILE_TREE)
    response.headers["x-page"] = str(page)
    response.headers["x-per-page"] = str(per_page)
    response.headers["x-total"] = str(len(MOCK_FILE_TREE))
    response.headers["x-total-pages"] = "1"
    
    return response


@app.get("/api/v4/projects/{project_id}/repository/files/{file_path:path}/raw")
async def get_file_raw(
    project_id: str,
    file_path: str,
    private_token: Optional[str] = Header(None, alias="Private-Token"),
    ref: str = Query("main")
):
    """
    获取文件原始内容
    """
    logger.info(f"Received request for file: project={project_id}, file={file_path}, ref={ref}")
    
    # 验证项目是否存在
    try:
        pid = int(project_id)
        if not any(p["id"] == pid for p in MOCK_PROJECTS):
            raise HTTPException(status_code=404, detail="Project not found")
    except ValueError:
        raise HTTPException(status_code=404, detail="Invalid project ID")
    
    # 解码文件路径
    from urllib.parse import unquote
    decoded_file_path = unquote(file_path)
    
    # 模拟不同文件的内容
    if decoded_file_path.lower() == "readme.md":
        logger.info("Returning README.md content")
        return MOCK_README
    elif decoded_file_path.endswith(".py"):
        logger.info(f"Returning mock Python file content for {decoded_file_path}")
        return f'# {decoded_file_path}\n\ndef main():\n    print("Hello from {decoded_file_path}")\n\nif __name__ == "__main__":\n    main()\n'
    elif decoded_file_path.endswith(".json"):
        logger.info(f"Returning mock JSON file content for {decoded_file_path}")
        return '{\n  "name": "test-config",\n  "version": "1.0.0"\n}\n'
    elif decoded_file_path.endswith(".txt"):
        logger.info(f"Returning mock text file content for {decoded_file_path}")
        return f'Content of {decoded_file_path}\n'
    else:
        logger.error(f"File not found: {decoded_file_path}")
        raise HTTPException(status_code=404, detail="File not found")


@app.options("/api/v4/{path:path}")
async def options_handler(path: str):
    """处理OPTIONS请求"""
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, PATCH, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Private-Token, Authorization",
        }
    )


if __name__ == "__main__":
    print("=" * 60)
    print("Mock GitLab API Server")
    print("=" * 60)
    print("Server will start on: http://localhost:9090")
    print("API endpoint: http://localhost:9090/api/v4")
    print("")
    print("Available mock projects:")
    for project in MOCK_PROJECTS:
        print(f"  - {project['path_with_namespace']} (ID: {project['id']})")
    print("")
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    # 启动服务器
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=9090,
        log_level="info"
    )
