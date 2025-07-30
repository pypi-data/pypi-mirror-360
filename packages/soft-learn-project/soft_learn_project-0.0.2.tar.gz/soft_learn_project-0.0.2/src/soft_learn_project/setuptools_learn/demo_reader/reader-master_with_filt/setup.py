from setuptools import setup, find_packages

setup(
    name="reader_wjl_test",
    version="2.0.0",
    license='MIT',
    description='description abc',

    # ✅ 必需的关键扩展配置
    author="Your Name",  # 作者信息
    author_email="your@email.com",
    url="https://github.com/yourusername/reader_wjl_test",  # 项目主页

    # 🔍 发现包结构（自动查找所有包）
    packages=find_packages(),

    # 📦 正确声明依赖的方式（不是 requires）
    install_requires=[
        'feedparser>=6.0.8',
        'html2text>=2020.1.16'
    ],

    # 🧪 添加开发/测试专用依赖
    extras_require={
        'dev': ['pytest>=7.0', 'flake8'],
        'test': ['coverage'],
    },

    # 📚 添加长描述（支持Markdown）
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',

    # ⚙️ 设置包包含的额外文件
    include_package_data=True,

    # 🎯 添加命令行入口点（如果有）
    entry_points={
        'console_scripts': [
            'reader-wjl = reader_wjl.core:main'
        ]
    },

    # 🧩 分类信息（可选但推荐）
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],

    # 🐍 Python版本要求
    python_requires='>=3.6',
)
