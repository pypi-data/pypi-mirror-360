from setuptools import setup, find_packages

setup(
    name='mseep-moondream-mcp',
    version='1.0.2',
    description='FastMCP server for Moondream vision language model',
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
    install_requires=['fastmcp>=2.3.0', 'torch>=2.0.0', 'torchvision>=0.15.0', 'transformers>=4.30.0', 'pillow>=9.0.0', 'aiohttp>=3.8.0', 'aiofiles>=23.0.0', 'pyvips>=2.2.0', 'einops>=0.6.0', 'pydantic>=2.0.0', 'pydantic-settings>=2.0.0', 'python-dotenv>=1.0.0', 'click>=8.0.0', 'rich>=13.0.0'],
    keywords=['mseep', 'mcp', 'fastmcp', 'moondream', 'vision', 'language-model', 'ai', 'computer-vision', 'image-analysis'],
)
