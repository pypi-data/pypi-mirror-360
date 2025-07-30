from setuptools import setup, find_packages

setup(
    name='mseep-mcp-kql-server',
    version='2.0.1',
    description='AI-Powered MCP server for KQL query execution with intelligent schema memory and context assistance',
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
    install_requires=['pydantic>=2.0.0', 'typing-extensions>=4.0.0', 'tabulate>=0.9.0', 'fastmcp>=2.0.0', 'mcp>=1.9.0', 'azure-kusto-data>=4.0.0', 'azure-identity>=1.15.0', 'azure-core>=1.29.0', 'httpx>=0.25.0', 'requests>=2.31.0', 'tenacity>=8.0.0', 'click>=8.0.0', 'colorama>=0.4.6', 'python-dotenv>=1.0.0'],
    keywords=['mseep', 'mcp', 'model-context-protocol', 'kql', 'kusto', 'azure', 'data-explorer', 'ai', 'schema-memory', 'query-execution', 'azure-data-explorer', 'claude', 'anthropic', 'intelligent-caching', 'data-analytics'],
)
