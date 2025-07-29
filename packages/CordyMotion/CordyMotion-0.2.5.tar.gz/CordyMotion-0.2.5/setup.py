from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.develop import develop
import os
from pathlib import Path
import shutil
import sys
import subprocess

class CustomInstallCommand(install):
    """自定义安装命令处理配置文件和本地依赖"""
    def run(self):
        # 标准安装
        install.run(self)
        # 先安装依赖
        self.install_dependencies()
        # 部署配置
        self.deploy_config()

    def install_dependencies(self):
        """安装本地依赖"""
        try:
            import importlib.resources as pkg_resources
            with pkg_resources.path('CordyMotion', 'cordymotioncaller-0.1.0-py3-none-any.whl') as whl_path:
                if whl_path.exists():
                    subprocess.check_call([sys.executable, "-m", "pip", "install", str(whl_path)])
        except Exception as e:
            print(f"安装依赖失败: {str(e)}", file=sys.stderr)
            raise

    def deploy_config(self):
        """部署配置文件"""
        try:
            import importlib.resources as pkg_resources
            with pkg_resources.path('CordyMotion', 'cordy.ini') as config_src:
                config_dest = Path.home() / "Bin/Config/cordy.ini"
                config_dest.parent.mkdir(parents=True, exist_ok=True)

                if not config_dest.exists():
                    shutil.copy(str(config_src), str(config_dest))
                    config_dest.chmod(0o644)  # rw-r--r--
                    print(f"Config file installed to: {config_dest}")
                else:
                    print(f"Config file already exists, not overwritten: {config_dest}")
        except Exception as e:
            print(f"部署配置文件失败: {str(e)}", file=sys.stderr)

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 处理本地依赖
def get_dependencies():
    deps = []
    if os.path.exists("deps/cordymotioncaller-0.1.0-py3-none-any.whl"):
        deps.append("cordymotioncaller @ file://localhost/{}/deps/cordymotioncaller-0.1.0-py3-none-any.whl".format(os.getcwd()))
    return deps


def _post_install():
    """安装后复制配置文件"""
    config_src = os.path.join(os.path.dirname(__file__), 'CordyMotion', 'cordy.ini')
    config_dest = str(Path.home() / "Bin/Config/cordy.ini")

    # 确保目标目录存在
    os.makedirs(os.path.dirname(config_dest), exist_ok=True)

    # 仅当目标文件不存在时才复制
    if not os.path.exists(config_dest):
        shutil.copy(config_src, config_dest)
        print(f"配置文件已部署到: {config_dest}")
    else:
        print(f"配置文件已存在，未覆盖: {config_dest}")


# 在setup()之后立即执行
_post_install()

setup(
    name="CordyMotion",
    version="0.2.5",
    author="Adam",
    author_email="haiyang.sun@cordy.com.cn",
    description="A package providing Cordy Motion libs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/CordyMotion",
    packages=find_packages(),
    package_data={
        'CordyMotion': [
            'cordy.ini',
            #'cordymotioncaller-0.1.0-py3-none-any.whl'
        ],
    },

    # cmdclass={
    #     'install': CustomInstallCommand,
    # },
    python_requires=">=3.10",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    # install_requires=[
    #     'cordymotioncaller>=0.2.0',
    # ],
    include_package_data=True,
    data_files=[
        (str(Path.home() / 'Bin/Config'), ['CordyMotion/cordy.ini']),
    ],
)