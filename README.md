# hb-base

HuanBei 基础库 — 提供给其他项目作为依赖使用的通用工具包。

## 项目结构

```
hb-base/
├── pyproject.toml          # 项目配置 & 包元信息
├── build_cython.py         # Cython 编译脚本
├── .gitlab-ci.yml          # CI/CD 配置（自动编译 .so + 发布）
├── .gitignore
├── src/
│   └── hb_base/            # 包源码
│       ├── __init__.py     # 包入口，暴露 __version__
│       ├── config.py       # 通用配置基类
│       ├── config.pyi      # 类型存根（IDE 补全用）
│       ├── logger.py       # 日志工具
│       ├── logger.pyi
│       ├── utils.py        # 通用工具函数
│       └── utils.pyi
└── tests/
    └── test_utils.py
```

## 本地开发

```bash
# 创建虚拟环境
python3.12 -m venv .venv
source .venv/bin/activate

# 安装开发依赖（包含 cython）
pip install -e ".[dev]"
# 或使用 uv
uv sync

# 运行测试
pytest
```

---

## 源码保护：Cython 编译为 .so

发布时通过 Cython 将 `.py` 源码编译为 `.so` 二进制文件，**别人安装后看不到源代码**。

### 工作原理

| 本地开发 | 发布包 |
|---------|--------|
| `.py` 源码，正常编辑和调试 | `.so` 二进制，无法阅读源码 |
| — | `.pyi` 存根，提供 IDE 代码提示 |
| `__init__.py` 保留 | `__init__.py` 保留（仅含版本号） |

### 构建流程

```bash
# 1. 编译 .py → .so
python build_cython.py

# 2. 删除源码（模拟 CI 流程）
find src/hb_base -name "*.py" ! -name "__init__.py" -delete

# 3. 打包
python -m build

# 4. 清理（恢复源码用于继续开发）
git checkout -- src/hb_base/
```

### 跨平台：cibuildwheel 多平台构建

`.so` 文件是**平台相关的**，本项目使用 `cibuildwheel` 在 CI 中**同时为 3 个平台编译**：

| 平台 | 编译产物 | CI Runner |
|------|---------|-----------|
| Linux x86_64 | `.cpython-312-x86_64-linux-gnu.so` | Docker（默认可用） |
| macOS ARM + x86 | `.cpython-312-darwin.so` | macOS Runner |
| Windows x64 | `.cpython-312-win_amd64.pyd` | Windows Runner |

打一个 tag 后，CI 并行编译所有平台，发布到 Package Registry。

用户执行 `pip install hb-base` 时，**pip 自动选择匹配当前平台的 wheel**，无需手动指定。

### 发布后的 wheel 文件（每个平台一个）

```
# Linux
hb_base-0.1.0-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl

# macOS ARM (M1/M2/M3)
hb_base-0.1.0-cp312-cp312-macosx_11_0_arm64.whl

# macOS Intel
hb_base-0.1.0-cp312-cp312-macosx_10_9_x86_64.whl

# Windows
hb_base-0.1.0-cp312-cp312-win_amd64.whl
```

每个 wheel 内部结构相同：
```
hb_base/__init__.py     ← 仅版本号
hb_base/config.so/.pyd  ← 编译后的二进制
hb_base/config.pyi      ← 类型提示（IDE 补全）
hb_base/logger.so/.pyd
hb_base/logger.pyi
hb_base/utils.so/.pyd
hb_base/utils.pyi
```

### CI 配置方案

**方案一：GitLab CI（当前配置 `.gitlab-ci.yml`）**

```
Build Linux   → 需要 Docker runner（默认有）
Build macOS   → 需要 macOS runner（需自建，打 macos tag）
Build Windows → 需要 Windows runner（需自建，打 windows tag）
```

如果没有 macOS/Windows runner，对应 job 会自动跳过（`allow_failure: true`），不影响 Linux 发布。

**方案二：GitHub Actions（备选，`.github/workflows/build.yml`）**

GitHub 免费提供 macOS/Windows/Linux runner，无需自建。适合：
- GitLab 没有 macOS/Windows runner
- 想要零成本覆盖所有平台

使用方式：将代码镜像到 GitHub，打 tag 后自动触发构建。

### 添加 macOS/Windows GitLab Runner（可选）

如果想在 GitLab CI 中构建 macOS/Windows，需要在对应机器上注册 GitLab Runner：

```bash
# 在 macOS 机器上
brew install gitlab-runner
gitlab-runner register --tag-list macos

# 在 Windows 机器上（PowerShell 管理员）
# 下载 gitlab-runner.exe 后
.\gitlab-runner.exe register --tag-list windows
```

### 添加新模块时的操作

1. 创建 `src/hb_base/new_module.py`（源码）
2. 创建 `src/hb_base/new_module.pyi`（类型存根）
3. 本地开发正常使用 `.py`
4. 发布时 CI 自动编译为 `.so`

`.pyi` 文件模板：

```python
# src/hb_base/new_module.pyi
"""模块文档字符串。"""

def my_function(name: str) -> str:
    """函数文档字符串。"""
    ...

class MyClass:
    """类文档字符串。"""
    def __init__(self, value: int) -> None: ...
    def do_something(self) -> str: ...
```

---

## 如何作为依赖包给第三方项目使用

有 **3 种方式** 可以让其他项目依赖 `hb-base`：

### 方式一：Git 依赖（推荐 — 最简单）

在目标项目的 `pyproject.toml` 中直接通过 Git 地址引用：

```toml
[project]
dependencies = [
  # SSH 方式（推荐）
  "hb-base @ git+ssh://git@your-gitlab.com/huanbei/hb-base.git@v0.1.0",

  # HTTPS 方式
  "hb-base @ git+https://your-gitlab.com/huanbei/hb-base.git@v0.1.0",

  # 指定分支
  "hb-base @ git+ssh://git@your-gitlab.com/huanbei/hb-base.git@main",

  # 指定 commit
  "hb-base @ git+ssh://git@your-gitlab.com/huanbei/hb-base.git@abc1234",
]
```

> **注意**：通过 Git 安装的是原始源码（`.py`），不会经过 Cython 编译。
> 如需发布编译后的 `.so` 版本，请使用方式二（Package Registry）。

安装：
```bash
pip install -e .
# 或
uv sync
```

### 方式二：GitLab Package Registry（推荐 — 正式发布）

通过 GitLab 内置的包管理器发布版本化的包（编译后的 .so 版本），其他项目按版本号安装。

#### 1. 发布到 GitLab Package Registry

在 `hb-base` 项目中打 tag 触发 CI 自动发布：

```bash
git tag v0.1.0
git push origin v0.1.0
```

CI 自动执行：Cython 编译 → 删除源码 → 打包 wheel → 发布到 Registry。

#### 2. 在目标项目中配置 Registry

在 `pyproject.toml` 中：

```toml
[project]
dependencies = [
  "hb-base==0.1.0",
]

[tool.uv]
extra-index-url = ["https://__token__:${CI_JOB_TOKEN}@your-gitlab.com/api/v4/projects/<hb-base-project-id>/packages/pypi/simple/"]
```

> **注意**：`<hb-base-project-id>` 是 hb-base 项目在 GitLab 中的数字 ID，可在项目 Settings > General 中找到。

#### 3. CI 环境变量

在 GitLab CI 中，`CI_JOB_TOKEN` 会自动注入：

```yaml
# 目标项目的 .gitlab-ci.yml
variables:
  PIP_EXTRA_INDEX_URL: "https://gitlab-ci-token:${CI_JOB_TOKEN}@your-gitlab.com/api/v4/projects/<hb-base-project-id>/packages/pypi/simple/"
```

### 方式三：本地路径依赖（仅开发用）

开发调试时，可以引用本地路径：

```toml
[project]
dependencies = [
  "hb-base @ file:///Users/liangyuxiang/Documents/work/feisu/_partner/huanbei/hb-base",
]
```

或使用 `uv` 的 workspace 功能：

```toml
# hbplayground/pyproject.toml
[tool.uv.sources]
hb-base = { path = "../hb-base" }
```

---

## 实际示例：在 hbplayground 中使用 hb-base

### 第 1 步：修改 hbplayground 的 pyproject.toml

```toml
[project]
name = "hb-plus"
version = "0.1.0"
requires-python = ">=3.12, <3.13"
dependencies = [
  # ... 原有依赖 ...
  "hb-base @ git+ssh://git@your-gitlab.com/huanbei/hb-base.git@v0.1.0",  # 新增
]
```

开发阶段也可以用本地路径：

```toml
[tool.uv.sources]
hb-base = { path = "../hb-base" }
```

### 第 2 步：安装依赖

```bash
cd /Users/liangyuxiang/Documents/work/feisu/_partner/huanbei/hbplayground
uv sync
```

### 第 3 步：在代码中使用

```python
# 在 hbplayground 的任意文件中
from hb_base import __version__
from hb_base.utils import greet
from hb_base.logger import get_logger
from hb_base.config import AppSettings

# 使用工具函数
message = greet("hbplayground")
print(message)  # Hello from hb-base, hbplayground!

# 使用日志
log = get_logger("hbplayground")
log.info("Application started")

# 继承配置基类
class MySettings(AppSettings):
    db_url: str = "postgresql://..."
    redis_url: str = "redis://..."

settings = MySettings()
```

---

## 版本发布流程

1. 更新 `src/hb_base/__init__.py` 中的 `__version__`
2. 更新 `pyproject.toml` 中的 `version`
3. 同步更新所有 `.pyi` 存根文件
4. 提交代码并打 tag：
   ```bash
   git add .
   git commit -m "feat: bump version to 0.2.0"
   git tag v0.2.0
   git push origin main --tags
   ```
5. CI 自动：Cython 编译 → 删除源码 → 打包 → 发布到 GitLab Package Registry
6. 下游项目更新依赖版本号即可获取新版本

## 版本号规范

遵循 [语义化版本](https://semver.org/lang/zh-CN/)：

- `0.x.x` — 初始开发阶段，API 可能随时变更
- `x.y.z` — 正式版本
  - **主版本号 (x)**：不兼容的 API 变更
  - **次版本号 (y)**：向下兼容的功能新增
  - **修订号 (z)**：向下兼容的问题修复
