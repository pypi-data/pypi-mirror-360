#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MQTT设备交互库安装脚本
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="aioeway",
    version="1.0.3",
    author="PuuuTao",
    author_email="kevinwang960105@gmail.com",
    description="一个基于异步编程的MQTT设备通信库",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/PuuuTao/aioeway",
    packages=find_packages(),  
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "device-mqtt-example=aioeway.example:main",  
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Hardware",
        "Topic :: Communications",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
