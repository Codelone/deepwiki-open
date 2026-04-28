#!/bin/bash
# GitLab代理API测试 - cURL命令示例
# 可以直接运行这些命令来手动测试API

echo "============================================================"
echo "GitLab 代理 API 测试 - cURL 命令示例"
echo "============================================================"
echo ""

# 配置
API_BASE="http://localhost:8001"
GITLAB_BASE="http://localhost:9090"
TOKEN="test-token-123456"

echo "配置:"
echo "  后端API: $API_BASE"
echo "  GitLab:  $GITLAB_BASE"
echo "  Token:   $TOKEN"
echo ""

# 测试1: API健康检查
echo "============================================================"
echo "测试1: API健康检查"
echo "============================================================"
curl -s "$API_BASE/health" | python3 -m json.tool
echo ""
echo ""

# 测试2: 获取项目列表
echo "============================================================"
echo "测试2: 获取项目列表"
echo "============================================================"
curl -s -H "PRIVATE-TOKEN: $TOKEN" \
  "$API_BASE/api/gitlab/proxy?base_url=$GITLAB_BASE&path=projects" \
  | python3 -m json.tool
echo ""
echo ""

# 测试3: 获取项目详情
echo "============================================================"
echo "测试3: 获取项目详情 (test-group/test-project)"
echo "============================================================"
PROJECT_PATH=$(python3 -c "import urllib.parse; print(urllib.parse.quote('test-group/test-project', safe=''))")
curl -s -H "PRIVATE-TOKEN: $TOKEN" \
  "$API_BASE/api/gitlab/proxy?base_url=$GITLAB_BASE&path=projects/$PROJECT_PATH" \
  | python3 -m json.tool
echo ""
echo ""

# 测试4: 获取仓库文件树
echo "============================================================"
echo "测试4: 获取仓库文件树 (项目ID: 1)"
echo "============================================================"
curl -s -H "PRIVATE-TOKEN: $TOKEN" \
  "$API_BASE/api/gitlab/proxy?base_url=$GITLAB_BASE&path=projects/1/repository/tree&recursive=true&per_page=100" \
  | python3 -m json.tool
echo ""
echo ""

# 测试5: 获取README文件内容
echo "============================================================"
echo "测试5: 获取README.md文件内容"
echo "============================================================"
FILE_PATH=$(python3 -c "import urllib.parse; print(urllib.parse.quote('README.md', safe=''))")
curl -s -H "PRIVATE-TOKEN: $TOKEN" \
  "$API_BASE/api/gitlab/proxy?base_url=$GITLAB_BASE&path=projects/1/repository/files/$FILE_PATH/raw&ref=main"
echo ""
echo ""

echo "============================================================"
echo "测试完成"
echo "============================================================"
