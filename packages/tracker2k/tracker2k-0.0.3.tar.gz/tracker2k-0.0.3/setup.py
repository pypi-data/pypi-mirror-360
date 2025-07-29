from setuptools import setup, find_packages

setup(
    name="tracker2k",             # 包名（PyPI唯一标识）
    version="0.0.3",                 # 初始版本号
    author="bxplucky",
    author_email="bxplucky@gmail.com",
    description="A log tracking client integration code for OpenAI agents sdk",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/bxplucky/tracker2k",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",         # Python版本要求
    install_requires=[],              # 依赖库（如 requests）
    extras_require={
        "dev": ["pytest>=6.0"],      # 开发依赖
    },
)