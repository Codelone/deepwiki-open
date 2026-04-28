# GitLab 代理功能测试 - 快速开始

## 🚀 5分钟快速测试

### Windows用户

1. **打开命令提示符(CMD)或PowerShell**

2. **进入项目目录**
   ```cmd
   cd d:\workspace\deepwiki-open
   ```

3. **运行一键测试脚本**
   ```cmd
   test\run_proxy_test.bat
   ```

4. **查看结果**
   - 脚本会自动启动所有服务
   - 等待服务启动后按任意键运行测试
   - 查看测试结果

就这么简单! 🎉

---

### Linux/Mac用户

1. **打开终端**

2. **进入项目目录**
   ```bash
   cd /path/to/deepwiki-open
   ```

3. **添加执行权限(首次运行)**
   ```bash
   chmod +x test/run_proxy_test.sh
   chmod +x test/curl_test_examples.sh
   ```

4. **运行一键测试脚本**
   ```bash
   ./test/run_proxy_test.sh
   ```

5. **查看结果**
   - 脚本会自动启动所有服务
   - 自动运行所有测试
   - 测试完成后自动清理

完成! ✨

---

## 📋 测试包含什么?

脚本会自动:

1. ✅ 检查Python和必要依赖
2. ✅ 启动模拟GitLab服务器(端口9090)
3. ✅ 启动后端API服务(端口8001)
4. ✅ 运行7个测试用例
5. ✅ 显示详细的测试结果

---

## 🎯 预期看到什么?

成功时你会看到:

```
╔══════════════════════════════════════════════════════════╗
║               GitLab 代理功能测试套件                     ║
╚══════════════════════════════════════════════════════════╝

============================================================
测试1: API健康检查
============================================================
✓ API服务正常运行

[... 更多测试 ...]

总计: 7 个测试
通过: 7
失败: 0
成功率: 100.0%

🎉 所有测试通过!
```

---

## 🔧 手动测试(可选)

如果你想手动测试某个功能:

### Windows
```cmd
test\curl_test_examples.bat
```

### Linux/Mac
```bash
chmod +x test/curl_test_examples.sh
./test/curl_test_examples.sh
```

---

## ❌ 遇到问题?

### 端口被占用

**症状**: 端口8001或9090已被占用

**解决**:
```bash
# Windows - 查找占用端口的进程
netstat -ano | findstr :8001
netstat -ano | findstr :9090

# 结束进程(使用任务管理器或命令)
taskkill /F /PID <进程ID>

# Linux/Mac - 查找并结束进程
lsof -i :8001
lsof -i :9090
kill <进程ID>
```

### Python依赖缺失

**症状**: ModuleNotFoundError: No module named 'fastapi'

**解决**:
```bash
# 安装依赖
pip install fastapi uvicorn requests

# 或使用项目依赖文件
cd api
pip install -r requirements.txt
```

### 无法启动服务

**症状**: 服务启动失败

**解决**:
1. 检查Python是否正确安装: `python --version`
2. 检查是否在项目根目录
3. 检查防火墙设置
4. 查看错误日志

---

## 📚 更多信息

- **完整文档**: `GITLAB_PROXY_SOLUTION.md`
- **测试说明**: `test/README_PROXY_TEST.md`
- **API使用**: 参考 `GITLAB_PROXY_SOLUTION.md` 中的API使用指南

---

## 💡 提示

1. **首次运行**: 脚本会自动检查并安装缺失的依赖
2. **服务保持运行**: 测试后服务会继续运行,可以手动测试
3. **停止服务**: 关闭对应的命令行窗口或按Ctrl+C
4. **查看日志**: 服务窗口会显示实时日志

---

## ✨ 快速命令参考

```bash
# 一键测试(推荐)
test\run_proxy_test.bat          # Windows
./test/run_proxy_test.sh         # Linux/Mac

# 手动cURL测试
test\curl_test_examples.bat      # Windows
./test/curl_test_examples.sh     # Linux/Mac

# 单独启动服务
python test/mock_gitlab_server.py  # 模拟GitLab
cd api && python main.py           # 后端API

# 运行测试脚本
python test/test_gitlab_proxy.py   # 自动化测试
```

---

**准备好了吗? 让我们开始测试吧!** 🚀

只需运行一个命令即可验证所有功能是否正常工作。
