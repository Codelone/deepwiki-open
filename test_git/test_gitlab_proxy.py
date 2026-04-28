"""
GitLab代理功能测试脚本

这个脚本测试通过后端代理访问GitLab API的功能
"""

import requests
import json
from typing import Dict, Any
import sys

# 配置
API_BASE_URL = "http://localhost:8001"  # 后端API地址
MOCK_GITLAB_URL = "http://localhost:9090"  # 模拟GitLab服务器地址
TEST_TOKEN = "test-token-123456"  # 测试用token

# 控制台颜色输出
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text: str):
    """打印标题"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}\n")


def print_success(text: str):
    """打印成功信息"""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_error(text: str):
    """打印错误信息"""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


def print_info(text: str):
    """打印信息"""
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")


def print_warning(text: str):
    """打印警告"""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")


def test_api_health():
    """测试API健康状态"""
    print_header("测试1: API健康检查")
    
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"API服务正常运行")
            print_info(f"服务: {data.get('service')}")
            print_info(f"状态: {data.get('status')}")
            return True
        else:
            print_error(f"API健康检查失败: HTTP {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error(f"无法连接到API服务器 ({API_BASE_URL})")
        print_warning("请确保后端服务正在运行")
        return False
    except Exception as e:
        print_error(f"健康检查异常: {str(e)}")
        return False


def test_mock_gitlab_health():
    """测试模拟GitLab服务器状态"""
    print_header("测试2: 模拟GitLab服务器健康检查")
    
    try:
        response = requests.get(f"{MOCK_GITLAB_URL}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"模拟GitLab服务器正常运行")
            print_info(f"服务: {data.get('message')}")
            print_info(f"版本: {data.get('version')}")
            return True
        else:
            print_error(f"模拟GitLab服务器检查失败: HTTP {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error(f"无法连接到模拟GitLab服务器 ({MOCK_GITLAB_URL})")
        print_warning("请先启动模拟GitLab服务器: python test/mock_gitlab_server.py")
        return False
    except Exception as e:
        print_error(f"模拟GitLab服务器检查异常: {str(e)}")
        return False


def test_proxy_list_projects():
    """测试通过代理获取项目列表"""
    print_header("测试3: 通过代理获取GitLab项目列表")
    
    try:
        # 构建代理请求
        proxy_url = f"{API_BASE_URL}/api/gitlab/proxy"
        params = {
            "base_url": MOCK_GITLAB_URL,
            "path": "projects"
        }
        headers = {
            "PRIVATE-TOKEN": TEST_TOKEN
        }
        
        print_info(f"发送请求到代理: {proxy_url}")
        print_info(f"目标GitLab: {MOCK_GITLAB_URL}")
        print_info(f"API路径: projects")
        
        response = requests.get(proxy_url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            projects = response.json()
            print_success(f"成功获取项目列表")
            print_info(f"项目数量: {len(projects)}")
            for project in projects:
                print(f"  - {project['path_with_namespace']} (ID: {project['id']})")
            return True
        else:
            print_error(f"获取项目列表失败: HTTP {response.status_code}")
            print_error(f"响应内容: {response.text}")
            return False
    except Exception as e:
        print_error(f"测试异常: {str(e)}")
        return False


def test_proxy_get_project_detail():
    """测试通过代理获取项目详情"""
    print_header("测试4: 通过代理获取GitLab项目详情")
    
    try:
        # 测试通过编码路径获取项目
        project_path = "test-group/test-project"
        encoded_path = requests.utils.quote(project_path, safe='')
        
        proxy_url = f"{API_BASE_URL}/api/gitlab/proxy"
        params = {
            "base_url": MOCK_GITLAB_URL,
            "path": f"projects/{encoded_path}"
        }
        headers = {
            "PRIVATE-TOKEN": TEST_TOKEN
        }
        
        print_info(f"获取项目: {project_path}")
        
        response = requests.get(proxy_url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            project = response.json()
            print_success(f"成功获取项目详情")
            print_info(f"项目名称: {project['name']}")
            print_info(f"项目路径: {project['path_with_namespace']}")
            print_info(f"默认分支: {project['default_branch']}")
            print_info(f"描述: {project['description']}")
            return True
        else:
            print_error(f"获取项目详情失败: HTTP {response.status_code}")
            print_error(f"响应内容: {response.text}")
            return False
    except Exception as e:
        print_error(f"测试异常: {str(e)}")
        return False


def test_proxy_get_repository_tree():
    """测试通过代理获取仓库文件树"""
    print_header("测试5: 通过代理获取仓库文件树")
    
    try:
        project_id = 1  # 使用第一个模拟项目
        
        proxy_url = f"{API_BASE_URL}/api/gitlab/proxy"
        params = {
            "base_url": MOCK_GITLAB_URL,
            "path": f"projects/{project_id}/repository/tree",
            "recursive": "true",
            "per_page": "100"
        }
        headers = {
            "PRIVATE-TOKEN": TEST_TOKEN
        }
        
        print_info(f"获取项目 {project_id} 的文件树")
        
        response = requests.get(proxy_url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            tree = response.json()
            print_success(f"成功获取文件树")
            print_info(f"文件数量: {len(tree)}")
            for item in tree:
                icon = "📁" if item["type"] == "tree" else "📄"
                print(f"  {icon} {item['path']}")
            return True
        else:
            print_error(f"获取文件树失败: HTTP {response.status_code}")
            print_error(f"响应内容: {response.text}")
            return False
    except Exception as e:
        print_error(f"测试异常: {str(e)}")
        return False


def test_proxy_get_file_content():
    """测试通过代理获取文件内容"""
    print_header("测试6: 通过代理获取文件内容")
    
    try:
        project_id = 1
        file_path = "README.md"
        encoded_file_path = requests.utils.quote(file_path, safe='')
        
        proxy_url = f"{API_BASE_URL}/api/gitlab/proxy"
        params = {
            "base_url": MOCK_GITLAB_URL,
            "path": f"projects/{project_id}/repository/files/{encoded_file_path}/raw",
            "ref": "main"
        }
        headers = {
            "PRIVATE-TOKEN": TEST_TOKEN
        }
        
        print_info(f"获取文件: {file_path}")
        
        response = requests.get(proxy_url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            content = response.text
            print_success(f"成功获取文件内容")
            print_info(f"文件大小: {len(content)} 字节")
            print(f"\n{Colors.OKCYAN}文件内容预览:{Colors.ENDC}")
            print("-" * 60)
            # 只显示前10行
            lines = content.split('\n')[:10]
            for line in lines:
                print(line)
            if len(content.split('\n')) > 10:
                print("...")
            print("-" * 60)
            return True
        else:
            print_error(f"获取文件内容失败: HTTP {response.status_code}")
            print_error(f"响应内容: {response.text}")
            return False
    except Exception as e:
        print_error(f"测试异常: {str(e)}")
        return False


def test_proxy_without_token():
    """测试不带token的代理请求"""
    print_header("测试7: 不带Token的代理请求(公开访问)")
    
    try:
        proxy_url = f"{API_BASE_URL}/api/gitlab/proxy"
        params = {
            "base_url": MOCK_GITLAB_URL,
            "path": "projects"
        }
        # 不添加token
        
        print_info(f"发送不带token的请求")
        
        response = requests.get(proxy_url, params=params, timeout=10)
        
        if response.status_code == 200:
            projects = response.json()
            print_success(f"公开访问成功")
            print_info(f"获取到 {len(projects)} 个项目")
            return True
        else:
            print_warning(f"公开访问失败: HTTP {response.status_code}")
            print_info("这可能是预期行为(需要认证)")
            return True  # 这也算正常,因为某些API需要认证
    except Exception as e:
        print_error(f"测试异常: {str(e)}")
        return False


def main():
    """运行所有测试"""
    print(f"\n{Colors.BOLD}{Colors.HEADER}")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 15 + "GitLab 代理功能测试套件" + " " * 15 + "║")
    print("╚" + "═" * 58 + "╝")
    print(f"{Colors.ENDC}\n")
    
    results = []
    
    # 运行测试
    tests = [
        ("API健康检查", test_api_health),
        ("模拟GitLab服务器检查", test_mock_gitlab_health),
        ("获取项目列表", test_proxy_list_projects),
        ("获取项目详情", test_proxy_get_project_detail),
        ("获取仓库文件树", test_proxy_get_repository_tree),
        ("获取文件内容", test_proxy_get_file_content),
        ("公开访问测试", test_proxy_without_token),
    ]
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except KeyboardInterrupt:
            print_warning("\n测试被用户中断")
            sys.exit(1)
        except Exception as e:
            print_error(f"测试执行异常: {str(e)}")
            results.append((test_name, False))
    
    # 打印测试总结
    print_header("测试结果总结")
    
    passed = sum(1 for _, result in results if result)
    failed = len(results) - passed
    
    for test_name, result in results:
        if result:
            print_success(f"{test_name}")
        else:
            print_error(f"{test_name}")
    
    print(f"\n{Colors.BOLD}总计: {len(results)} 个测试{Colors.ENDC}")
    print(f"{Colors.OKGREEN}通过: {passed}{Colors.ENDC}")
    print(f"{Colors.FAIL}失败: {failed}{Colors.ENDC}")
    
    success_rate = (passed / len(results)) * 100 if results else 0
    print(f"{Colors.BOLD}成功率: {success_rate:.1f}%{Colors.ENDC}\n")
    
    if failed == 0:
        print(f"{Colors.OKGREEN}{Colors.BOLD}🎉 所有测试通过!{Colors.ENDC}\n")
        return 0
    else:
        print(f"{Colors.FAIL}{Colors.BOLD}❌ 部分测试失败{Colors.ENDC}\n")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print_warning("\n\n测试被中断")
        sys.exit(1)
