from setuptools import setup, find_packages

setup(
    name='mseep-mcp-task-orchestrator',
    version='1.8.0',
    description='A Model Context Protocol server for task orchestration',
    long_description="Package managed by MseeP.ai",
    long_description_content_type="text/plain",
    author='mseep',
    author_email='support@skydeck.ai',
    maintainer='mseep',
    maintainer_email='support@skydeck.ai',
    url='https://github.com/EchoingVesper/mcp-task-orchestrator',
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=['mcp>=1.9.0', 'pydantic>=2.0.0  # Data validation and settings management', 'jinja2>=3.1.0', 'pyyaml>=6.0.0', 'aiofiles>=23.0.0', 'psutil>=5.9.0', 'filelock>=3.12.0', 'sqlalchemy>=2.0.0', 'alembic>=1.10.0', 'typer>=0.9.0  # CLI framework for command-line interface', 'rich>=13.0.0  # Rich terminal output formatting'],
    keywords=['mseep', 'mcp', 'ai', 'task-orchestration', 'claude', 'automation', 'llm', 'workflow'],
)
