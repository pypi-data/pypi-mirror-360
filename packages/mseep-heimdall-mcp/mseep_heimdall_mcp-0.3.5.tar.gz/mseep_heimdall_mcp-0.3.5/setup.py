from setuptools import setup, find_packages

setup(
    name='mseep-heimdall-mcp',
    version='0.3.5',
    description='Persistent, project-aware, long-term memory for AI coding assistants',
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
    install_requires=['onnxruntime>=1.16.0', 'tokenizers>=0.21.0', 'qdrant-client>=1.7.0', 'numpy>=1.24.0', 'loguru>=0.7.0', 'python-dotenv>=1.0.0', 'pydantic>=2.0.0', 'typer>=0.9.0', 'rich>=13.0.0', 'docker>=6.0.0', 'psutil>=5.9.0', 'requests>=2.31.0', 'prompt-toolkit>=3.0.0', 'platformdirs>=3.0.0', 'portalocker>=2.7.0', 'mcp>=1.4.0', 'GitPython', 'spacy', 'vaderSentiment', 'nrclex>=3.0.0'],
    keywords=['mseep', 'ai', 'memory', 'cognitive', 'llm', 'mcp', 'quadrant', 'persistent', 'session', 'chat'],
)
