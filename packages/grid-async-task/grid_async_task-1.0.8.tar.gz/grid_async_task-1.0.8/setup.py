#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 直接定义依赖，不依赖外部文件
requirements = [
    # 核心依赖
    "pika>=1.3.0",              # RabbitMQ客户端
    "PyMySQL>=1.0.2",           # MySQL数据库驱动
    "SQLAlchemy>=1.4.0",        # ORM框架
    "python-dotenv>=0.19.0",    # 环境变量管理
    
    # HTTP客户端
    "requests>=2.25.0",         # HTTP请求库
    "aiohttp>=3.8.0",           # 异步HTTP客户端
    
    # 日志和配置
    "loguru>=0.6.0",            # 高级日志库
    
    # 数据处理
    "pydantic>=1.8.0",          # 数据验证
    "pydantic-settings>=2.0.0",  # Pydantic设置管理
    
    # 工具库
    "tenacity>=8.0.0",          # 重试库
    "click>=8.0.0",             # 命令行工具
]

# 如果存在requirements.txt文件，则尝试从中读取依赖
if os.path.exists("requirements.txt"):
    try:
        with open("requirements.txt", "r", encoding="utf-8") as fh:
            file_requirements = []
            for line in fh:
                line = line.strip()
                # 跳过空行和注释行
                if line and not line.startswith("#"):
                    # 处理带注释的依赖行，只保留包名和版本部分
                    if "#" in line:
                        line = line.split("#")[0].strip()
                    if line:  # 确保处理后的行不为空
                        file_requirements.append(line)
            
            if file_requirements:
                print(f"从requirements.txt读取到 {len(file_requirements)} 个依赖包")
                # 打印读取到的依赖包（调试用）
                for req in file_requirements:
                    print(f"  - {req}")
                requirements = file_requirements
            else:
                print("requirements.txt文件为空或只包含注释，使用默认依赖")
    except Exception as e:
        print(f"读取requirements.txt失败，使用默认依赖: {e}")
else:
    print("未找到requirements.txt文件，使用默认依赖")

setup(
    name="grid-async-task",
    version="1.0.8",
    author="grid",
    author_email="grid@example.com",
    description="一个通用的异步任务处理插件，支持RabbitMQ队列监听、任务重试、进度通知等功能",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitee.com/shenzhen-grid/grid-async-task-plugin",
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
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "grid-task=grid_async_task.cli:main",
        ],
    },
    package_data={
        "grid_async_task": ["sql/*.sql"],
    },
    include_package_data=True,
) 