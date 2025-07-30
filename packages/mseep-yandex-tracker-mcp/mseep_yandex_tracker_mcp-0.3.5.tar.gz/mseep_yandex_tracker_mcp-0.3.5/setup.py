from setuptools import setup, find_packages

setup(
    name='mseep-yandex-tracker-mcp',
    version='0.3.5',
    description='Yandex Tracker MCP Server',
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
    install_requires=['aiocache[redis]>=0.12.3', 'aiohttp>=3.11.18', 'mcp[cli]>=1.10.0', 'pydantic>=2.11.3', 'pydantic-settings>=2.8.1', 'python-dateutil>=2.9.0.post0', 'yarl>=1.20.0'],
    keywords=['mseep'],
)
