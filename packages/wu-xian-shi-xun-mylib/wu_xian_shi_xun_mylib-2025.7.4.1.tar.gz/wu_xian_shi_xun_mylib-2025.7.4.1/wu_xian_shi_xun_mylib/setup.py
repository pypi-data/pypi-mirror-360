from setuptools import setup, find_packages
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

setup(
    name="mylib",
    version="0.8",
    packages=["mylib"],
)
