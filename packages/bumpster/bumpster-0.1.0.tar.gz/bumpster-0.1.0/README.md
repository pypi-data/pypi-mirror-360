# bumpster

专为 Python 项目设计的智能语义化版本管理命令行工具。

## 简介

`bumpster` 是一个遵循 PEP 440 规范的 Python 项目版本管理工具。它可以自动更新项目版本号，创建 Git 提交和标签，简化版本发布流程。

## 主要功能

- ✅ 完全遵循 PEP 440 版本规范
- ✅ 支持 pyproject.toml 和 setup.py
- ✅ 支持预发布版本（alpha、beta、rc、dev、post）
- ✅ 自动 Git 集成（提交、标签、推送）
- ✅ 交互式命令行界面
- ✅ 内置版本号验证功能
- ✅ 安全检查（分支、工作区状态）

## 安装

```bash
# 使用 uv 全局安装
uv tool install bumpster
```

### 开发安装

```bash
# 克隆仓库
git clone https://github.com/yarnovo/bumpster-py.git
cd bumpster-py

# 安装依赖
uv sync

# 全局安装开发版本（类似 npm link）
uv tool install -e .
```

## 使用方法

### 版本升级

在项目根目录运行：

```bash
# 主命令
bump

# 别名
bump-py
```

工具会自动：
1. 检测当前版本
2. 提供交互式选项
3. 更新配置文件
4. 创建 Git 提交和标签
5. 推送到远程仓库（可选）

### 干跑模式

使用 `--dry-run` 选项预览操作而不实际执行：

```bash
# 预览版本更新操作
bump --dry-run
```

干跑模式会：
- 显示所有将要执行的操作
- 不修改任何文件
- 不创建 Git 提交或标签
- 不推送到远程仓库
- 完全无副作用，安全预览

### 版本验证

使用 `validate` 子命令验证版本号是否符合 PEP 440 规范：

```bash
# 验证版本号
bump validate 1.0.0
bump validate 1.0.0a0
bump-py validate 2.0.0.dev1

# 输出示例
✅ Version 1.0.0 is PEP 440 compliant  # 退出码 0
❌ Version 'invalid' is not PEP 440 compliant  # 退出码 1
```

在 CI/CD 中使用：

```bash
# 在 shell 脚本中
if bump validate "$VERSION"; then
  echo "版本号有效"
else
  echo "版本号无效"
  exit 1
fi

# 或使用 Python 模块
python -m bump_version.cli validate 1.0.0
```

## 版本格式

遵循 PEP 440 规范的版本号格式：

```
1.0.0          # 正式版本
1.0.0a0        # Alpha 版本
1.0.0b0        # Beta 版本
1.0.0rc0       # Release Candidate
1.0.0.dev0     # 开发版本
1.0.0.post0    # 后发布版本
```

## 配置文件支持

### pyproject.toml（推荐）

```toml
[project]
name = "my-package"
version = "1.0.0"

# 或 Poetry 项目
[tool.poetry]
name = "my-package" 
version = "1.0.0"
```

### setup.py

```python
setup(
    name="my-package",
    version="1.0.0",
    ...
)
```

## 工作流程示例

### 基本发布流程

```bash
# 1. 开发完成，准备发布新版本
bump
# 选择 "正式版本 (Production)"
# 选择 "Patch (修订号)"
# 版本：1.0.0 → 1.0.1

# 2. 自动完成
# - 更新 pyproject.toml
# - git commit -m "chore: release 1.0.1"
# - git tag v1.0.1
# - git push --follow-tags
```

### 预发布流程

```bash
# 1. 创建 Alpha 版本
bump
# 选择 "Alpha 版本"
# 选择 "Minor (次版本号)"
# 版本：1.0.0 → 1.1.0a0

# 2. 升级到 Beta
bump
# 选择 "Beta 版本"
# 版本：1.1.0a0 → 1.1.0b0

# 3. 发布正式版
bump
# 选择 "正式版本 (Production)"
# 版本：1.1.0b0 → 1.1.0
```

## 环境变量

- `BUMP_VERSION_SKIP_PUSH`: 设置为任意值时跳过 git push

## API 使用

在代码中使用版本验证功能：

```python
from bump_version.cli import validate_version

if validate_version("1.0.0"):
    print("版本号有效")
else:
    print("版本号无效")
```

## 注意事项

1. 使用前确保：
   - 项目已初始化 Git 仓库
   - 工作区干净（无未提交的更改）
   - 在主分支（main/master）上操作

2. 版本号规范：
   - 必须符合 PEP 440 规范
   - 不要手动添加 'v' 前缀（工具会自动处理）

3. Git 标签格式：
   - 自动添加 'v' 前缀：v1.0.0

## 文档

- [测试指南](TESTING.md) - 本地测试和全局安装说明
- [开发指南](DEVELOPMENT.md) - 开发环境设置和工作流程
- [部署指南](DEPLOYMENT.md) - 发布和部署流程

## 许可证

ISC