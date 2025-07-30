from setuptools import setup, find_packages

setup(
    name='mseep-ocode',
    version='0.1.0',
    description='Terminal-native AI coding assistant powered by Ollama models',
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
    install_requires=['aiohttp>=3.9', 'click>=8.1', 'rich>=13', 'gitpython>=3.1', 'tree-sitter>=0.20', 'pydantic>=2', 'pyyaml>=6', 'prompt-toolkit>=3', 'aiofiles>=23', 'watchdog>=3', 'pexpect>=4.9.0', 'psutil>=5.9.0', 'jsonpath-ng>=1.5.3', 'python-dotenv>=1.0.0', 'requests>=2.31.0'],
    keywords=['mseep'],
)
