from setuptools import setup, find_packages

setup(
    name='mseep-monarch-mcp-server',
    version='0.1.0',
    description='Model Context Protocol (MCP) server for Monarch Money personal finance platform',
    long_description="Package managed by MseeP.ai",
    long_description_content_type="text/plain",
    author='mseep',
    author_email='support@skydeck.ai',
    maintainer='mseep',
    maintainer_email='support@skydeck.ai',
    url='https://github.com/mseep',
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=['mcp[cli]>=1.0.0', 'monarchmoney>=0.1.12', 'python-dotenv>=1.0.0', 'pydantic>=2.0.0', 'asyncio>=3.4.3'],
    keywords=['mseep'],
)
