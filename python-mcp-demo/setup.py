#!/usr/bin/env python3
"""
Setup configuration for claude-stats-mcp package
"""

from setuptools import setup, find_packages
import os

# 读取 README
readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
if os.path.exists(readme_path):
    with open(readme_path, 'r', encoding='utf-8') as f:
        long_description = f.read()
else:
    long_description = 'MCP server for Claude Code usage statistics'

# 读取 requirements.txt
requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
with open(requirements_path, 'r', encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='claude-stats-mcp',
    version='1.0.0',
    description='MCP server for querying Claude Code usage statistics',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Your Name',
    author_email='your.email@example.com',
    url='https://github.com/yourusername/claude-stats-mcp',
    license='MIT',

    # 包配置
    packages=find_packages(),
    py_modules=['server'],
    include_package_data=True,

    # 依赖
    install_requires=requirements,

    # Python 版本要求
    python_requires='>=3.8',

    # CLI 入口点
    entry_points={
        'console_scripts': [
            'claude-stats-mcp=server:main',
        ],
    },

    # PyPI 分类
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Software Development :: Libraries',
        'Topic :: Communications',
    ],

    # 关键词
    keywords='mcp claude statistics fastmcp model-context-protocol',

    # 项目链接
    project_urls={
        'Bug Reports': 'https://github.com/yourusername/claude-stats-mcp/issues',
        'Source': 'https://github.com/yourusername/claude-stats-mcp',
        'Documentation': 'https://github.com/yourusername/claude-stats-mcp#readme',
    },
)
