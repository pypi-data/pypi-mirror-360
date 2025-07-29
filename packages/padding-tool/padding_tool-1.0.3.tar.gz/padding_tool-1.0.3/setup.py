"""Module setup"""
from setuptools import setup

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="padding-tool",
    version="1.0.3",
    py_modules=["padding_tool"],
    install_requires=["requests"],
    entry_points={
        'console_scripts': [
            'padding-tool = padding_tool:main',
        ],
    },
    author="Gil Weisbord",
    description="A simple Python CLI tool to pad a binary file to a specified size using a given byte value.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.6',
)
