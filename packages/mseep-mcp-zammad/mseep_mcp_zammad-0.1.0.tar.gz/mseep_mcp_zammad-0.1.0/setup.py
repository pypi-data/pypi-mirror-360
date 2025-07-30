from setuptools import setup, find_packages

setup(
    name='mseep-mcp-zammad',
    version='0.1.0',
    description='Model Context Protocol server for Zammad ticket system integration (unofficial)',
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
    install_requires=['mcp>=1.0.0', 'zammad-py>=3.2.0', 'pydantic>=2.0.0', 'python-dotenv>=1.0.0', 'httpx>=0.25.0'],
    keywords=['mseep', 'mcp', 'zammad', 'tickets', 'support', 'api'],
)
