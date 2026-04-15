# hb-base

HuanBei 基础库 — 提供给其他项目作为依赖使用的通用工具包。

## 项目结构

```
hb-base/
├── pyproject.toml          # 项目配置 & 包元信息
├── .gitlab-ci.yml          # CI/CD 配置
├── .gitignore
├── src/
│   └── hb_base/            # 包源码
│       ├── __init__.py     # 包入口，暴露 __version__
│       ├── config.py       # 通用配置基类
│       ├── logger.py       # 日志工具
│       └── utils.py        # 通用工具函数
└── tests/
    └── test_utils.py       # 测试
```

## 本地开发

```bash
# 创建虚拟环境
python3.12 -m venv .venv
source .venv/bin/activate

# 安装开发依赖
pip install -e ".[dev]"
# 或使用 uv
uv sync

# 运行测试
pytest
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

安装：
```bash
pip install -e .
# 或
uv sync
```

### 方式二：GitLab Package Registry（推荐 — 正式发布）

通过 GitLab 内置的包管理器发布版本化的包，其他项目按版本号安装。

#### 1. 发布到 GitLab Package Registry

在 `hb-base` 项目中打 tag 触发 CI 自动发布：

```bash
git tag v0.1.0
git push origin v0.1.0
```

CI 会自动执行 `python -m build` + `twine upload` 将包发布到 GitLab Package Registry。

#### 2. 在目标项目中配置 Registry

在目标项目（如 hbplayground）根目录创建或编辑 `~/.pypirc` 或在 `pip` 中配置：

```bash
# 方法 A：通过 pip 配置（推荐）
pip config set global.extra-index-url "https://__token__:${CI_JOB_TOKEN}@your-gitlab.com/api/v4/projects/<hb-base-project-id>/packages/pypi/simple/"
```

或在 `pyproject.toml` 中：

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

在 GitLab CI 中，`CI_JOB_TOKEN` 会自动注入，可以直接使用：

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

```tomll
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
3. 提交代码并打 tag：
   ```bash
   git add .
   git commit -m "feat: bump version to 0.2.0"
   git tag v0.2.0
   git push origin main --tags
   ```
4. CI 自动构建并发布到 GitLab Package Registry
5. 下游项目更新依赖版本号即可获取新版本

## 版本号规范

遵循 [语义化版本](https://semver.org/lang/zh-CN/)：

- `0.x.x` — 初始开发阶段，API 可能随时变更
- `x.y.z` — 正式版本
  - **主版本号 (x)**：不兼容的 API 变更
  - **次版本号 (y)**：向下兼容的功能新增
  - **修订号 (z)**：向下兼容的问题修复
