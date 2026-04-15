"""
Cython 构建脚本 — 将 .py 编译为 .so 二进制扩展模块。

使用方式：
    python build_cython.py          # 编译
    python build_cython.py --clean  # 清理编译产物
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
    # 清理 .so 文件
    for f in SRC.rglob("*.so"):
        f.unlink()
    for f in SRC.rglob("*.c"):
        if f.name != "__init__.c":  # 保留手写的 .c 文件
            f.unlink()
    # 清理 egg-info
    for d in ROOT.glob("*.egg-info"):
        shutil.rmtree(d)
    for d in SRC.glob("*.egg-info"):
        shutil.rmtree(d)
    print("Cleaned build artifacts.")


def build_ext():
    """使用 Cython 编译 .py → .so。"""
    from Cython.Build import cythonize
    from setuptools import Extension, setup

    # 收集所有需要编译的 .py 文件（排除 __init__.py，保留为纯文本以暴露版本号）
    py_files = [str(f) for f in SRC.rglob("*.py") if f.name != "__init__.py"]

    if not py_files:
        print("No .py files found to compile.")
        return

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

    print(f"\nCompiled {len(py_files)} files to .so extensions.")


if __name__ == "__main__":
    if "--clean" in sys.argv:
        clean()
    else:
        build_ext()
