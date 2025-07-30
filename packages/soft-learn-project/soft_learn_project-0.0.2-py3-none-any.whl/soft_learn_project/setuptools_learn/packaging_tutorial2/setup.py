from setuptools import setup, find_packages

setup(
    name="mytest2",          # 包名（pip安装时使用的名称）
    version="0.1.0",            # 版本号
    author="Your Name",
    description="A short description",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),   # 自动发现包
    install_requires=[          # 依赖包列表
    ],
    python_requires=">=3.6",    # Python版本要求
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
