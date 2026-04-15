"""
自定义 setup.py — 标记此包包含二进制扩展模块。

Cython 编译后的 .so 文件不会自动被 setuptools 识别为扩展模块，
导致生成纯 Python wheel (py3-none-any.whl)。
通过 BinaryDistribution 强制 setuptools 生成平台特定的 wheel tag。
"""

from setuptools import Distribution


class BinaryDistribution(Distribution):
    """强制将包含 .so/.pyd 的包标记为平台特定。"""

    def has_ext_modules(self):
        return True


def build(setup_kwargs):
    setup_kwargs.update(distclass=BinaryDistribution)


from setuptools import setup  # noqa: E402

setup(distclass=BinaryDistribution)
