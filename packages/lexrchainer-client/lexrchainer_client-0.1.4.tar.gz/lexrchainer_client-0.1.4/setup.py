from setuptools import setup, find_packages

setup(
    name="lexrchainer-client",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.0.0",
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
    ],
    author="LexrChainer Team",
    author_email="team@lexrchainer.com",
    description="A Python client library for interacting with the LexrChainer API",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/lexrchainer/client",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
) 