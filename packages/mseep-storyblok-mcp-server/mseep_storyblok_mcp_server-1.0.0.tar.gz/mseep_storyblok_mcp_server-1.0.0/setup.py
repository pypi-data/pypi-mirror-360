from setuptools import setup, find_packages

setup(
    name='mseep-storyblok-mcp-server',
    version='1.0.0',
    description='MCP server for storyblok',
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
    install_requires=['httpx>=0.28.1', 'mcp[cli]>=1.9.4', 'python-dotenv>=1.1.0', 'requests>=2.32.4'],
    keywords=['mseep'],
)
