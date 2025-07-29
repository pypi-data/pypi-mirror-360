# -*- coding: utf-8 -*-
"""
@Author   : 清澈
@Time     :2024/3/25
@File     :setup.py.py
@IDE      :PyCharm
"""

import setuptools  # 导入setuptools打包工具

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="eeo",  # 包名
    version="1.0.7",  # 包版本号，便于维护版本,保证每次发布都是版本都是唯一的
    author="QH",  # 作者，可以写自己的姓名
    author_email="eeoapisupport@eeoa.com",  # 作者联系方式，可写自己的邮箱地址
    description="eeo ClassInAPI包",  # 包的简述
    long_description=long_description,  # 包的详细介绍，一般在README.md文件内
    long_description_content_type="text/markdown",
    url="https://github.com/Qingche99/eeoAPI",  # 自己项目地址，比如github的项目地址
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',  # 对python的最低版本要求
)

