from setuptools import setup, find_packages

setup(
    name='mseep-mxcp',
    version='0.3.0',
    description='Enterprise MCP framework for building production AI tools with SQL/Python, featuring security, audit trails, and policy enforcement',
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
    install_requires=['mcp>=1.9.0', 'click>=8.1.7', 'pyyaml>=6.0.1', 'jsonschema', 'duckdb>=0.9.2', 'jinja2>=3.1.3', 'aiohttp>=3.8.0', 'starlette>=0.27.0', 'makefun', 'pandas>=2.0.0', 'posthog>=3.0.0', 'dbt-core>=1.6.0', 'dbt-duckdb>=1.6.0', 'cel-python>=0.2.0', 'httpx>=0.25.0'],
    keywords=['mseep'],
)
