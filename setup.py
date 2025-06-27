from setuptools import setup, find_packages

setup(
    name="myutils",
    version="0.2",
    packages=find_packages(),
    author="Kenneth Copas",
    description="A collection of personal utility functions",
    install_requires=[
        "langchain",
        "langchain-community",
        "langchain-openai",
        "langchain-chroma",
        "openai",
        "requests",
        "flask",
        "mysql-connector-python"
    ]
)
