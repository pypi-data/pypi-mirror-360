import os
from setuptools import setup, find_packages

# 读取README.md作为长描述
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 项目元数据
setup(
    name="auto_video_mcp",
    version="0.1.1",
    description="飞影数字人API服务，提供数字人相关功能",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fancyboi999/auto_video_mcp",
    project_urls={
        "Bug Tracker": "https://github.com/fancyboi999/auto_video_mcp/issues",
        "Documentation": "https://github.com/fancyboi999/auto_video_mcp/docs",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.11",
    install_requires=[
        "fastapi>=0.110.0",
        "mcp[cli]>=1.6.0",
        "pydantic>=2.11.3",
        "requests>=2.32.3",
        "sqlalchemy>=2.0.30",
        "uvicorn>=0.34.2",
    ],
    extras_require={
        "dev": [
            "build>=1.2.2.post1",
            "setuptools>=45",
            "twine>=6.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "auto_video_mcp=auto_video_mcp.server:main",
        ],
    },
) 