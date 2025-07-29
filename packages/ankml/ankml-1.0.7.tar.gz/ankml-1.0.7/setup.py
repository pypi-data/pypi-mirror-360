#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ANKML库安装脚本

这是ANKML（Advanced Neural Knowledge for Malware Learning）库的安装脚本。
ANKML是一个专业的恶意软件检测库，提供多种预训练模型和易用的API。

作者: ANKML团队
联系: AX3721@outlook.com
网站: ankml.top
"""

from setuptools import setup, find_packages
import os

# 读取README文件
try:
    with open("readme.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "Advanced Neural Knowledge for Malware Learning - 专业的恶意软件检测库"

# 读取requirements文件
try:
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]
except FileNotFoundError:
    requirements = ["numpy", "requests", "onnxruntime"]

setup(
    name="ankml",
    version="1.0.7",
    author="ANKML Team",
    author_email="AX3721@outlook.com",
    description="Advanced Neural Knowledge for Malware Learning - 恶意软件检测库",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://ankml.top",
    project_urls={
        "Bug Tracker": "https://github.com/your_username/ankml/issues",
        "Documentation": "https://ankml.top/docs",
        "Source Code": "https://github.com/your_username/ankml",
        "Website": "https://ankml.top"
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Security",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "gui": [
            "tkinter",
        ],
        "web": [
            "flask>=2.0",
            "flask-cors>=3.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "ankml=ankml.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "ankml": [
            "*.json",
            "*.md",
        ],
    },
    keywords=[
        "malware", "detection", "security", "machine learning", 
        "artificial intelligence", "cybersecurity", "antivirus",
        "neural network", "deep learning", "threat detection"
    ],
    license="MIT",
    zip_safe=False,
)