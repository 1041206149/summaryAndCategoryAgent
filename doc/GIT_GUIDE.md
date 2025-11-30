# Git 使用指南

## .gitignore 说明

`.gitignore` 文件已配置，会自动忽略以下内容：

### 已忽略的文件/目录

✅ **Python相关**
- `__pycache__/` - Python缓存
- `*.pyc`, `*.pyo` - 编译文件
- `.pytest_cache/` - pytest缓存
- `*.egg-info/` - 包信息

✅ **环境配置**
- `.env` - 本地环境变量（包含敏感信息）
- `venv/`, `env/` - 虚拟环境

✅ **IDE配置**
- `.idea/` - PyCharm配置
- `.vscode/` - VS Code配置

✅ **系统文件**
- `.DS_Store` - macOS文件
- `Thumbs.db` - Windows文件

✅ **日志和缓存**
- `*.log` - 日志文件
- `.cache/` - 缓存目录

✅ **Claude Code**
- `.claude/` - Claude Code运行时数据

### 需要提交的文件

✅ **源代码**
- 所有 `.py` 文件
- 所有 `__init__.py` 文件

✅ **配置文件**
- `.env.example` - 环境变量示例（不包含敏感信息）
- `requirements.txt` - 依赖列表

✅ **数据文件**
- `data/小结分类.csv` - 分类数据

✅ **文档**
- 所有 `.md` 文件

## 初始化Git仓库

### 1. 初始化仓库
```bash
cd /Users/brown/Projects/summaryAndCategory
git init
```

### 2. 添加所有文件
```bash
git add .
```

### 3. 查看将要提交的文件
```bash
git status
```

### 4. 创建初始提交
```bash
git commit -m "Initial commit: LangChain refactored conversation analysis system

- Implemented modular architecture with 6 layers
- Added LangChain integration with qwen-max model
- Created comprehensive documentation
- All tests passing (5/5)
- Version: 2.0.0"
```

## 连接远程仓库

### GitHub
```bash
# 创建远程仓库后
git remote add origin https://github.com/yourusername/summaryAndCategory.git
git branch -M main
git push -u origin main
```

### GitLab
```bash
git remote add origin https://gitlab.com/yourusername/summaryAndCategory.git
git branch -M main
git push -u origin main
```

### Gitee (国内)
```bash
git remote add origin https://gitee.com/yourusername/summaryAndCategory.git
git branch -M main
git push -u origin main
```

## 常用Git命令

### 查看状态
```bash
git status              # 查看当前状态
git log --oneline      # 查看提交历史
git diff               # 查看未暂存的修改
```

### 提交更改
```bash
git add .              # 添加所有修改
git add <file>         # 添加特定文件
git commit -m "消息"   # 提交修改
git push               # 推送到远程
```

### 分支管理
```bash
git branch             # 查看分支
git branch dev         # 创建dev分支
git checkout dev       # 切换到dev分支
git checkout -b feat   # 创建并切换到feat分支
git merge dev          # 合并dev分支到当前分支
```

### 拉取更新
```bash
git pull               # 拉取远程更新
git fetch              # 获取远程更新（不合并）
```

## 推荐的提交信息格式

使用语义化提交信息：

```bash
# 新功能
git commit -m "feat: 添加批量处理功能"

# 修复bug
git commit -m "fix: 修复分类重试逻辑错误"

# 文档更新
git commit -m "docs: 更新API文档"

# 重构
git commit -m "refactor: 优化LLM客户端初始化逻辑"

# 性能优化
git commit -m "perf: 优化对话清洗性能"

# 测试
git commit -m "test: 添加分类Agent单元测试"

# 配置
git commit -m "chore: 更新依赖版本"
```

## Git工作流建议

### 1. 功能分支工作流
```bash
# 从main创建功能分支
git checkout -b feature/batch-processing

# 开发并提交
git add .
git commit -m "feat: 实现批量处理API"

# 推送到远程
git push -u origin feature/batch-processing

# 在GitHub/GitLab创建Pull Request/Merge Request
# 代码审查通过后合并到main
```

### 2. 快速修复
```bash
# 从main创建修复分支
git checkout -b hotfix/classification-bug

# 修复并提交
git add .
git commit -m "fix: 修复一级分类错误"

# 推送并合并
git push -u origin hotfix/classification-bug
```

## .gitignore 最佳实践

### 永远不要提交
❌ 敏感信息（API密钥、密码）
❌ 本地环境配置（`.env`）
❌ IDE配置文件
❌ 编译文件和缓存
❌ 日志文件
❌ 虚拟环境

### 应该提交
✅ 源代码
✅ 配置示例（`.env.example`）
✅ 依赖列表（`requirements.txt`）
✅ 文档
✅ 必要的数据文件
✅ 测试代码

## 检查.gitignore是否生效

```bash
# 查看将要提交的文件（dry-run）
git add -n .

# 查看已忽略的文件
git status --ignored

# 检查特定文件是否被忽略
git check-ignore -v .env
```

## 紧急情况：已提交敏感文件

如果不小心提交了`.env`等敏感文件：

```bash
# 1. 从Git历史中移除（保留本地文件）
git rm --cached .env

# 2. 提交移除操作
git commit -m "chore: 移除敏感配置文件"

# 3. 如果已推送到远程，需要强制推送（危险操作！）
git push --force

# 4. 更换所有暴露的密钥和凭据
```

## 常见问题

### Q: .gitignore不生效？
```bash
# 清除Git缓存
git rm -r --cached .
git add .
git commit -m "chore: 更新.gitignore"
```

### Q: 如何查看忽略了哪些文件？
```bash
git status --ignored
```

### Q: 如何强制添加被忽略的文件？
```bash
git add -f <file>
```

## 团队协作建议

1. **统一.gitignore**: 确保团队使用相同的.gitignore
2. **代码审查**: 使用Pull Request进行代码审查
3. **分支保护**: 保护main分支，禁止直接推送
4. **自动化**: 使用CI/CD自动运行测试

## 参考资源

- [Git官方文档](https://git-scm.com/doc)
- [GitHub .gitignore模板](https://github.com/github/gitignore)
- [语义化版本](https://semver.org/lang/zh-CN/)
- [约定式提交](https://www.conventionalcommits.org/zh-hans/)
