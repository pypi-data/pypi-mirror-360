#!/usr/bin/env python
# coding: utf-8

from setuptools import setup

with open("README.md", "r", encoding='utf8') as fh:
    long_description = fh.read()

package_dir = {
    'ex_cd': 'ex_cd'
}

setup(
    name='ex_cd',
    version='1.16.4',
    author='yindaheng98',
    author_email='yindaheng98@163.com',
    url='https://github.com/yindaheng98/ex-cd',
    description=u'高效下载E站gallery的所有历史数据',
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_dir=package_dir,
    packages=[key for key in package_dir],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'gallery-dl',
    ],
)
