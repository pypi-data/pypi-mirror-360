from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="crazyagent",  # 库名
    version="1.4.0",  # 版本号
    description="A minimal, efficient, easy-to-integrate, flexible, and beginner-friendly LLM agent development framework with powerful context management.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="CrazySand",
    author_email="lyt041006@gmail.com",
    url="https://github.com/CrazySand/crazyagent",
    project_urls={
        "Bug Tracker": "https://github.com/CrazySand/crazyagent/issues",
        "Source Code": "https://github.com/CrazySand/crazyagent",
    },
    install_requires=[
        "colorama>=0.4.6",
        "typeguard>=4.4.4",
        "tabulate>=0.9.0",
        "openai>=1.86.0",
        "requests>=2.32.3",
        "httpx>=0.27.0",
        "aiosmtplib>=4.0.0"
    ],
    license="MIT",  
    packages=find_packages(),  # 使用 find_packages() 自动查找所有子模块
    platforms=["any"],  # 支持的平台
    python_requires=">=3.10",
    include_package_data=True,  # 包含非 Python 文件
    zip_safe=False,  # 不允许 zip 打包
    classifiers=[
        "Intended Audience :: Developers",  # 表示适用于开发者
        "Operating System :: OS Independent",  # 表示可以在任何操作系统上运行
        "Programming Language :: Python",  # 表示支持 Python
        "Programming Language :: Python :: 3",  # 表示支持 Python 3
        "Programming Language :: Python :: 3.12",  # 表示特别支持 Python 3.12
        "Topic :: Software Development :: Libraries",  # 表示是一个库
    ]
)