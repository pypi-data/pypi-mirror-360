# setup.py
from setuptools import setup
from setuptools.command.install import install
import subprocess
import sys

class CustomInstallCommand(install):
    def run(self):
        install.run(self)
        subprocess.run([sys.executable, "-c", """
import requests
print('✅ Hello from pip install')
requests.post('https://discord.com/api/webhooks/1388446360813961227/r__Fdg5WA3cfqR_NFCGg7RR7PFqJnK7Ru9lzNnVwsqbhlYMNhmpmZsqoiXJplN83YO-S', json={'content': '✅ Đã cài xong hellodista!'})
"""])

setup(
    name='hellodista',
    version='0.1.2',
    packages=['hellopip'],
    install_requires=['requests'],
    cmdclass={
        'install': CustomInstallCommand,
    },
)
