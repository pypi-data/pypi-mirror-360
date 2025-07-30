from setuptools import setup, find_packages

setup(
    name='mseep-magg',
    version='0.7.1',
    description='MCP Aggregator',
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
    install_requires=['fastmcp>=2.8.0', 'aiohttp>=3.12.13', 'pydantic>=2.11.7', 'pydantic-settings>=2.10.0', 'rich>=14.0.0', 'prompt-toolkit>=3.0.51', 'cryptography>=45.0.4', 'pyjwt>=2.10.1', 'watchdog>=6.0.0', 'art>=6.5'],
    keywords=['mseep', 'model', 'context', 'protocol', 'ai', 'agent', 'mcp', 'aggregator', 'proxy', 'fastmcp', 'aiohttp', 'pydantic', 'pydantic-settings', 'rich'],
)
