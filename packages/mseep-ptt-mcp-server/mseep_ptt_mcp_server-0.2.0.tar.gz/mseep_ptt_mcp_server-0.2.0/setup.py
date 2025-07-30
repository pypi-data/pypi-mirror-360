from setuptools import setup, find_packages

setup(
    name='mseep-ptt-mcp-server',
    version='0.2.0',
    description='The best MCP server for PTT.',
    long_description="Package managed by MseeP.ai",
    long_description_content_type="text/plain",
    author='mseep',
    author_email='support@skydeck.ai',
    maintainer='mseep',
    maintainer_email='support@skydeck.ai',
    url='https://github.com/PyPtt/ptt_mcp_server',
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=['pyptt', 'fastmcp', 'python-dotenv'],
    keywords=['mseep'],
)
