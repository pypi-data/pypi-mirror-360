#!/usr/bin/env python
# -*- coding:utf-8 -*-

import setuptools

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()
setuptools.setup(
    name="TDhelper",
    version="2.8.23",
    keywords=("pip", "TDhelper", "featureextraction"),
    description="fix rpc call don't know mater service bug.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="Apache 2.0",
    url="https://gitee.com/TonyDon/pyLib",
    author="TangJing",
    author_email="yeihizhi@163.com",
    packages=setuptools.find_packages(exclude=["UnitTest"]),
    classifiers=[],
    install_requires=[
        "crypto==1.4.1",
        "openpyxl==3.1.2",
        "pymongo==4.3.3",
        "requests==2.28.2",
        "six==1.16.0",
        "urllib3==1.26.15",
        "mysql-connector>=2.2.9"
],
entry_points = {
        'console_scripts': [
            #'foo = demo:test',
            #'bar = demo:test',
            'saas = TDhelper.shellScripts.saasHelper:CMD'
        ],
        'gui_scripts': [
            #'baz = demo:test',
        ]
    }
)
