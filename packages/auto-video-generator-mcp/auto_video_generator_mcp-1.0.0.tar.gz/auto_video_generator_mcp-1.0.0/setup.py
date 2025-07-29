#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os

# 读取README文件
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# 读取requirements.txt
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="auto-video-generator-mcp",
    version="1.0.0",
    author="zgmurder",
    author_email="zgmurder@example.com",  # 请替换为你的邮箱
    description="基于MCP协议的智能视频生成工具，支持自动字幕、语音合成、运动检测等功能",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/zgmurder/auto_video_generator-mcp",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Video",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
    },
    entry_points={
        "console_scripts": [
            "auto-video-generator=auto_generate_video_mcp_modular:main",
        ],
    },
    include_package_data=True,
    package_data={
        "auto_video_modules": ["*.json", "*.ttf", "*.otf"],
    },
    keywords="video generation, subtitle, speech synthesis, motion detection, mcp",
    project_urls={
        "Bug Reports": "https://github.com/zgmurder/auto_video_generator-mcp/issues",
        "Source": "https://github.com/zgmurder/auto_video_generator-mcp",
        "Documentation": "https://github.com/zgmurder/auto_video_generator-mcp#readme",
    },
) 