from setuptools import setup, find_packages

setup(
    name='mseep-synalinks',
    version='1.0.0',
    description='Graph-Based Programmable Neuro-Symbolic LM Framework',
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
    install_requires=['absl-py', 'asyncio', 'click', 'datasets', 'docstring-parser', 'graphviz', 'inquirer', 'jinja2', 'litellm', 'matplotlib', 'namex', 'neo4j', 'nest-asyncio', 'numpy', 'optree', 'pydantic', 'pydotplus', 'rich', 'sentry-sdk'],
    keywords=['mseep'],
)
