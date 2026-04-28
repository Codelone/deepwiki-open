@echo off
REM GitLab代理API测试 - cURL命令示例 (Windows)
REM 可以直接运行这些命令来手动测试API

setlocal

echo ============================================================
echo GitLab 代理 API 测试 - cURL 命令示例
echo ============================================================
echo.

REM 配置
set API_BASE=http://localhost:8001
set GITLAB_BASE=http://localhost:9090
set TOKEN=test-token-123456

echo 配置:
echo   后端API: %API_BASE%
echo   GitLab:  %GITLAB_BASE%
echo   Token:   %TOKEN%
echo.

REM 检查curl是否可用
curl --version >nul 2>&1
if errorlevel 1 (
    echo [错误] curl未安装或不在PATH中
    echo 请安装curl或使用Windows 10/11内置的curl
    pause
    exit /b 1
)

REM 测试1: API健康检查
echo ============================================================
echo 测试1: API健康检查
echo ============================================================
curl -s "%API_BASE%/health"
echo.
echo.

REM 测试2: 获取项目列表
echo ============================================================
echo 测试2: 获取项目列表
echo ============================================================
curl -s -H "PRIVATE-TOKEN: %TOKEN%" "%API_BASE%/api/gitlab/proxy?base_url=%GITLAB_BASE%&path=projects"
echo.
echo.

REM 测试3: 获取项目详情
echo ============================================================
echo 测试3: 获取项目详情 (test-group/test-project)
echo ============================================================
curl -s -H "PRIVATE-TOKEN: %TOKEN%" "%API_BASE%/api/gitlab/proxy?base_url=%GITLAB_BASE%&path=projects/test-group%%2Ftest-project"
echo.
echo.

REM 测试4: 获取仓库文件树
echo ============================================================
echo 测试4: 获取仓库文件树 (项目ID: 1)
echo ============================================================
curl -s -H "PRIVATE-TOKEN: %TOKEN%" "%API_BASE%/api/gitlab/proxy?base_url=%GITLAB_BASE%&path=projects/1/repository/tree&recursive=true&per_page=100"
echo.
echo.

REM 测试5: 获取README文件内容
echo ============================================================
echo 测试5: 获取README.md文件内容
echo ============================================================
curl -s -H "PRIVATE-TOKEN: %TOKEN%" "%API_BASE%/api/gitlab/proxy?base_url=%GITLAB_BASE%&path=projects/1/repository/files/README.md/raw&ref=main"
echo.
echo.

echo ============================================================
echo 测试完成
echo ============================================================
pause
