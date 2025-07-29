# setup.py
import setuptools
import os

def get_version_from_init():
    """Reads the __version__ from src/zk/__init__.py"""
    # 假设你的包是 src/pypi_demo
    # 确保这个路径是正确的，与你的项目结构相符
    init_path = os.path.join(os.path.dirname(__file__), 'src', 'zk', '__init__.py')
    with open(init_path, 'r') as f:
        for line in f:
            if line.startswith('__version__'):
                # 解析 'attribute = "value"' 或 "attribute = 'value'"
                return line.split('=')[1].strip().strip("'\"")
    raise RuntimeError("Unable to find __version__ string.")

setuptools.setup(
    # 在这里不指定 version，因为它会在 pyproject.toml 中被 dynamic = ["version"] 接管
    # 或者如果你想完全通过 setup.py 控制，可以这样：
    version=get_version_from_init(),
    # 你的其他 setuptools 配置可以放在这里，或者继续使用 pyproject.toml
    # 如果 pyproject.toml 和 setup.py 都定义了某些字段，setuptools 会合并它们
    # 通常建议元数据大部分在 pyproject.toml 中定义，setup.py 仅用于动态逻辑
)