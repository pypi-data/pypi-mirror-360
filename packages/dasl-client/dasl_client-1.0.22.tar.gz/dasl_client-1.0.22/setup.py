# setup.py

from setuptools import setup, find_packages

setup(
    name="dasl-client",
    version="0.0.0",
    author="Antimatter Team",
    author_email="support@antimatter.io",
    description="The DASL client library used for interacting with the DASL client.",
    long_description="TODO: Link to docs page or README.md.",
    long_description_content_type="text/markdown",
    url="https://github.com/antimatter/asl",
    packages=find_packages(),
    python_requires=">=3.8",
)
