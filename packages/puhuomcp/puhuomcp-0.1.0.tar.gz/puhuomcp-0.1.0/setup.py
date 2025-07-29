from setuptools import setup, find_packages

setup(
    name="puhuomcp",
    version="0.1.0",
    description="Waybill Intercept Demo MCP Service",
    author="duxuan",
    author_email="1126912882@qq.com",
    packages=find_packages(),
    install_requires=[
        "mcp",  # 这里写你的依赖
    ],
    entry_points={
        "console_scripts": [
            "puhuomcp = puhuomcp.main:main",
        ],
    },
    python_requires=">=3.7",
)