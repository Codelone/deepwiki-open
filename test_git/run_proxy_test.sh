#!/bin/bash
# GitLab代理功能测试 - 一键启动脚本 (Linux/Mac)
# 此脚本将依次启动所需的服务并运行测试

set -e

echo "============================================================"
echo "          GitLab 代理功能测试 - 自动化启动"
echo "============================================================"
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未检测到Python3,请先安装Python"
    exit 1
fi

echo "[1/4] 检查依赖..."
python3 -c "import fastapi" 2>/dev/null || {
    echo "[警告] FastAPI未安装,正在安装依赖..."
    pip3 install fastapi uvicorn requests
}

echo "[2/4] 启动模拟GitLab服务器 (端口9090)..."
cd "$(dirname "$0")/.."
python3 test/mock_gitlab_server.py > /tmp/mock_gitlab.log 2>&1 &
MOCK_PID=$!
sleep 3

echo "[3/4] 启动后端API服务 (端口8001)..."
cd api
python3 main.py > /tmp/deepwiki_api.log 2>&1 &
API_PID=$!
cd ..
sleep 5

echo "[4/4] 等待服务启动完成..."
sleep 3

echo ""
echo "============================================================"
echo "服务已启动:"
echo "  - 模拟GitLab服务器: http://localhost:9090 (PID: $MOCK_PID)"
echo "  - 后端API服务:       http://localhost:8001 (PID: $API_PID)"
echo "============================================================"
echo ""
echo "运行测试脚本..."
echo "============================================================"
echo ""

python3 test/test_gitlab_proxy.py
TEST_RESULT=$?

echo ""
echo "============================================================"
echo "测试完成"
echo "============================================================"
echo ""
echo "清理: 停止后台服务..."
kill $MOCK_PID 2>/dev/null || true
kill $API_PID 2>/dev/null || true

echo "服务已停止"
echo ""

exit $TEST_RESULT
