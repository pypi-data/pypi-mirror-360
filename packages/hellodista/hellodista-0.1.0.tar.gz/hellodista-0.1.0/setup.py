from setuptools import setup
from setuptools.command.install import install
import subprocess
import sys
import os

class PostInstallCommand(install):
    def run(self):
        install.run(self)
        subprocess.call([sys.executable, os.path.join(os.path.dirname(__file__), "hello.py")])

setup(
    name="hellodista",
    version="0.1.0",
    packages=["hellopip"],
    install_requires=["requests"],
    cmdclass={"install": PostInstallCommand},
    author="pwnkn0x",
    description="Hello world + webhook when pip installed",
    python_requires=">=3.6",
)
