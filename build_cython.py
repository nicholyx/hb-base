"""
Cython 构建脚本 — 将 .py 编译为 .so/.pyd 二进制扩展模块。

使用方式：
    python build_cython.py              # 编译 + 删除源码
    python build_cython.py --no-delete  # 仅编译，保留源码
    python build_cython.py --clean      # 清理编译产物
"""

import shutil
import sys
from pathlib import Path

# 项目根目录
ROOT = Path(__file__).parent
SRC = ROOT / "src" / "hb_base"
BUILD = ROOT / "build"
DIST = ROOT / "dist"


def clean():
    """清理所有编译产物。"""
    for d in [BUILD, DIST]:
        if d.exists():
            shutil.rmtree(d)
    for f in SRC.rglob("*.so"):
        f.unlink()
    for f in SRC.rglob("*.pyd"):
        f.unlink()
    for f in SRC.rglob("*.c"):
        if f.name != "__init__.c":
            f.unlink()
    for d in ROOT.glob("*.egg-info"):
        shutil.rmtree(d)
    for d in SRC.glob("*.egg-info"):
        shutil.rmtree(d)
    print("Cleaned build artifacts.")


def delete_sources():
    """删除已编译的 .py 源码文件（保留 __init__.py）。"""
    deleted = []
    for f in SRC.rglob("*.py"):
        if f.name == "__init__.py":
            continue
        f.unlink()
        deleted.append(f.name)
    if deleted:
        print(f"Deleted source files: {', '.join(deleted)}")


def build_ext():
    """使用 Cython 编译 .py → .so/.pyd。"""
    from Cython.Build import cythonize
    from setuptools import Extension, setup

    # 收集所有需要编译的 .py 文件（排除 __init__.py）
    py_files = [str(f) for f in SRC.rglob("*.py") if f.name != "__init__.py"]

    if not py_files:
        print("No .py files found to compile.")
        return False

    extensions = [
        Extension(
            f"hb_base.{Path(f).relative_to(SRC).with_suffix('').as_posix().replace('/', '.')}",
            [f],
        )
        for f in py_files
    ]

    setup(
        name="hb-base",
        ext_modules=cythonize(
            extensions,
            compiler_directives={"language_level": "3"},
            build_dir=str(BUILD),
        ),
        script_args=["build_ext", "--inplace"],
    )

    print(f"\nCompiled {len(py_files)} files to binary extensions.")
    return True


if __name__ == "__main__":
    args = set(sys.argv[1:])

    if "--clean" in args:
        clean()
    else:
        # 恢复源码（处理同一 runner 上多次构建的情况）
        import subprocess

        subprocess.run(["git", "checkout", "--", "src/hb_base/"], check=False)

        # 编译
        build_ext()

        # 默认删除源码（除非指定 --no-delete）
        if "--no-delete" not in args:
            delete_sources()
