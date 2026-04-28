# GitLab代理功能测试指南

本文档说明如何测试和验证GitLab代理功能是否正常工作。

## 📋 概述

由于企业内部环境限制,前端无法直接访问内网GitLab API(会遇到CORS跨域问题)。为解决这个问题,我们实现了后端代理功能,前端通过后端代理来访问GitLab API。

## 🏗️ 架构

```
前端 (Next.js)  →  后端代理 (FastAPI)  →  内网GitLab API
                   /api/gitlab/proxy
```

## 🚀 快速开始

### 1. 启动模拟GitLab服务器

首先,在一个终端窗口中启动模拟的GitLab服务器:

```bash
cd d:\workspace\deepwiki-open
python test/mock_gitlab_server.py
```

服务器将在 `http://localhost:9090` 启动,模拟内网GitLab环境。

你应该看到类似以下输出:
```
============================================================
Mock GitLab API Server
============================================================
Server will start on: http://localhost:9090
API endpoint: http://localhost:9090/api/v4

Available mock projects:
  - test-group/test-project (ID: 1)
  - demo-group/demo-repo (ID: 2)

Press Ctrl+C to stop the server
============================================================
```

### 2. 启动后端API服务

在另一个终端窗口中启动后端API:

```bash
cd d:\workspace\deepwiki-open\api
python main.py
```

后端服务将在 `http://localhost:8001` 启动。

### 3. 运行测试脚本

在第三个终端窗口中运行测试脚本:

```bash
cd d:\workspace\deepwiki-open
python test/test_gitlab_proxy.py
```

## 📝 测试内容

测试脚本将执行以下测试:

1. **API健康检查** - 验证后端API服务是否正常运行
2. **模拟GitLab服务器检查** - 验证模拟GitLab服务器是否正常运行
3. **获取项目列表** - 通过代理获取GitLab项目列表
4. **获取项目详情** - 通过代理获取特定项目的详细信息
5. **获取仓库文件树** - 通过代理获取项目的文件树结构
6. **获取文件内容** - 通过代理获取README.md等文件的内容
7. **公开访问测试** - 测试不带Token的请求

## 🔍 预期结果

所有测试都应该通过,你会看到类似以下的输出:

```
╔══════════════════════════════════════════════════════════╗
║               GitLab 代理功能测试套件                     ║
╚══════════════════════════════════════════════════════════╝

============================================================
测试1: API健康检查
============================================================

✓ API服务正常运行
ℹ 服务: deepwiki-api
ℹ 状态: healthy

...

============================================================
测试结果总结
============================================================

✓ API健康检查
✓ 模拟GitLab服务器检查
✓ 获取项目列表
✓ 获取项目详情
✓ 获取仓库文件树
✓ 获取文件内容
✓ 公开访问测试

总计: 7 个测试
通过: 7
失败: 0
成功率: 100.0%

🎉 所有测试通过!
```

## 🔧 代理API使用方法

### 基本用法

通过代理访问GitLab API的格式:

```
GET /api/gitlab/proxy?base_url={GitLab地址}&path={API路径}
```

### 参数说明

- `base_url`: GitLab服务器地址(例如: `http://cicdcoding.tlb.com`)
- `path`: GitLab API路径(例如: `projects` 或 `projects/1`)

### 示例

#### 1. 获取项目列表

```javascript
const response = await fetch(
  '/api/gitlab/proxy?base_url=http://localhost:9090&path=projects',
  {
    headers: {
      'PRIVATE-TOKEN': 'your-token-here'
    }
  }
);
```

#### 2. 获取项目详情

```javascript
const projectPath = encodeURIComponent('test-group/test-project');
const response = await fetch(
  `/api/gitlab/proxy?base_url=http://localhost:9090&path=projects/${projectPath}`,
  {
    headers: {
      'PRIVATE-TOKEN': 'your-token-here'
    }
  }
);
```

#### 3. 获取文件树

```javascript
const response = await fetch(
  '/api/gitlab/proxy?base_url=http://localhost:9090&path=projects/1/repository/tree&recursive=true',
  {
    headers: {
      'PRIVATE-TOKEN': 'your-token-here'
    }
  }
);
```

#### 4. 获取文件内容

```javascript
const filePath = encodeURIComponent('README.md');
const response = await fetch(
  `/api/gitlab/proxy?base_url=http://localhost:9090&path=projects/1/repository/files/${filePath}/raw&ref=main`,
  {
    headers: {
      'PRIVATE-TOKEN': 'your-token-here'
    }
  }
);
```

## 🐛 故障排除

### 问题1: 无法连接到API服务器

**错误信息**: `无法连接到API服务器 (http://localhost:8001)`

**解决方法**:
- 确保后端API服务正在运行
- 检查端口8001是否被占用
- 检查防火墙设置

### 问题2: 无法连接到模拟GitLab服务器

**错误信息**: `无法连接到模拟GitLab服务器 (http://localhost:9090)`

**解决方法**:
- 确保模拟GitLab服务器正在运行
- 检查端口9090是否被占用
- 先启动模拟服务器: `python test/mock_gitlab_server.py`

### 问题3: SSL验证错误

**解决方法**:
- 代理服务器已配置为禁用SSL验证(仅用于内网环境)
- 对于生产环境,建议配置正确的SSL证书

### 问题4: 代理请求超时

**解决方法**:
- 检查网络连接
- 增加超时时间(当前为30秒)
- 检查GitLab服务器是否响应

## 🔐 生产环境配置

在实际部署到生产环境时,需要:

1. **配置正确的GitLab地址**
   ```typescript
   const INTERNAL_GITLAB_URL = "http://cicdcoding.tlb.com";
   ```

2. **配置SSL证书**(如果GitLab使用HTTPS)
   - 在后端修改 `verify=False` 为 `verify=True`
   - 确保服务器信任GitLab的SSL证书

3. **配置认证Token**
   - 使用环境变量存储敏感信息
   - 不要在代码中硬编码Token

4. **添加错误处理和日志**
   - 生产环境应有完善的错误处理
   - 记录所有API请求日志便于调试

## 📚 相关文件

- `api/api.py` - 代理端点实现
- `test/mock_gitlab_server.py` - 模拟GitLab服务器
- `test/test_gitlab_proxy.py` - 测试脚本
- `src/app/[owner]/[repo]/page.tsx` - 前端使用示例

## 💡 提示

- 模拟服务器提供了基本的GitLab API功能,足以用于测试
- 可以根据需要在模拟服务器中添加更多项目和数据
- 测试脚本可以用作API使用的参考示例

## 📞 支持

如有问题,请检查:
1. 所有服务是否正常启动
2. 端口是否被占用
3. 网络连接是否正常
4. 日志输出中的错误信息
