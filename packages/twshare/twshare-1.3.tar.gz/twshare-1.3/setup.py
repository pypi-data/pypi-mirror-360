#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
Date: 2025/7/8 17:00
Desc: ThinkWide PYPI info file
"""
from setuptools import setup, find_packages

setup(
    name='twshare',
    version='1.3',
    packages=find_packages(),  # 自动查找包和子包
    install_requires=[],  # 依赖项列表（如果有的话）
    license="MIT",
    author='ThinkWide',
    author_emAIl='15115829@qq.com',
    description='twshare is an elegant and simple financial data interface library for Python, built for '
                'human beings! ',
    long_description='twshare is an elegant and simple financial data interface library for Python, '
                     'built for human beings!',
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    include_package_data=True,
    package_data={"": ["*.py", "*.json", "*.pk", "*.js", "*.zip"]},
)

'''
# 构建包（这将创建一个dist目录）
python setup.py sdist bdist_wheel

# 上传到PyPI（需要先配置~/.pypirc文件）
twine upload dist / *

'''
