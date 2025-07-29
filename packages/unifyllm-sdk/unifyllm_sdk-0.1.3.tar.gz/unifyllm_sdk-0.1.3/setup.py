#!/usr/bin/env python3
"""
Setup script for UniLLM library.
"""

import setuptools

with open("src/unillm/README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="unifyllm-sdk",
    version="0.1.3",
    author="Sahil Handa",
    author_email="sahilhanda@gmail.com",
    description="Unified Python client for multiple LLM providers (OpenAI, Anthropic, etc.) with drop-in compatibility.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sahilhd/unifyllm-sdk",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    install_requires=[
        "requests>=2.28.0",
        "pydantic>=2.0.0"
    ],
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    include_package_data=True,
    license="MIT",
) 