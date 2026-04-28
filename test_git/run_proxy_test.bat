@echo off
REM GitLab代理功能测试 - 一键启动脚本
REM 此脚本将依次启动所需的服务并运行测试

setlocal enabledelayedexpansion

echo ============================================================
echo           GitLab 代理功能测试 - 自动化启动
echo ============================================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python,请先安装Python
    pause
    exit /b 1
)

echo [1/4] 检查依赖...
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo [警告] FastAPI未安装,正在安装依赖...
    pip install fastapi uvicorn requests
)

echo [2/4] 启动模拟GitLab服务器 (端口9090)...
start "Mock GitLab Server" cmd /k "cd /d %~dp0 && python test\mock_gitlab_server.py"
timeout /t 3 /nobreak >nul

echo [3/4] 启动后端API服务 (端口8001)...
start "DeepWiki API Server" cmd /k "cd /d %~dp0\api && python main.py"
timeout /t 5 /nobreak >nul

echo [4/4] 等待服务启动完成...
timeout /t 3 /nobreak >nul

echo.
echo ============================================================
echo 服务已启动:
echo   - 模拟GitLab服务器: http://localhost:9090
echo   - 后端API服务:       http://localhost:8001
echo ============================================================
echo.
echo 按任意键运行测试...
pause >nul

echo.
echo ============================================================
echo 运行测试脚本...
echo ============================================================
echo.

python test\test_gitlab_proxy.py

echo.
echo ============================================================
echo 测试完成
echo ============================================================
echo.
echo 提示: 
echo   - 模拟GitLab服务器和后端API服务将继续运行
echo   - 关闭对应的命令行窗口可以停止服务
echo   - 或按 Ctrl+C 停止服务
echo.
pause
