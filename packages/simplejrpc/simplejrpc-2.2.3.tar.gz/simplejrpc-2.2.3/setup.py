# -*- encoding: utf-8 -*-
import os
from setuptools import find_packages, setup

# 确保 py.typed 存在
os.makedirs("simplejrpc", exist_ok=True)
open("simplejrpc/py.typed", "a").close()  # 创建空文件

setup(
    version="2.2.3",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown; charset=UTF-8",
    keywords=[
        "gm",
        "gm-sdk",
        "simplejrpc",
        "gmssh",
        "jsonrpc",
        "jsonrpcserver",
        "jsonrpcclient",
    ],
    python_requires=">=3.10",
    packages=find_packages(),
    package_data={"simplejrpc": ["py.typed"]},
    include_package_data=True,
    zip_safe=False,
    # exclude_package_date={"": [".gitignore"]},
    install_requires=[
        "jsonrpcclient==4.0.3",
        "jsonrpcserver==5.0.9",
        "loguru==0.7.3",
        "PyYAML==6.0.2",
        "WTForms==3.2.1",
    ],
)
