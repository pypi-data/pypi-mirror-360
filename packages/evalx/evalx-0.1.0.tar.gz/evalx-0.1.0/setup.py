#!/usr/bin/env python3
"""
Setup script for EvalX.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as f:
        return f.read()

# Read version from __init__.py
def get_version():
    version_file = os.path.join("evalx", "__init__.py")
    with open(version_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"').strip("'")
    return "0.1.0"

setup(
    name="evalx",
    version=get_version(),
    description="Next-generation evaluation framework for LLM applications",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Vishal Seelam",
    author_email="vishalseelam@gmail.com",
    url="https://github.com/vishalseelam/EvalX",
    packages=find_packages(where=".", include=["evalx*"]),
    package_dir={"": "."},
    python_requires=">=3.9",
    install_requires=[
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "scipy>=1.7.0",
        "scikit-learn>=1.0.0",
        "transformers>=4.20.0",
        "sentence-transformers>=2.2.0",
        "torch>=1.12.0",
        "nltk>=3.7",
        "rouge-score>=0.1.0",
        "bert-score>=0.3.0",
        "pydantic>=2.0.0",
        "typer>=0.9.0",
        "rich>=13.0.0",
        "tqdm>=4.64.0",
        "python-dotenv>=1.0.0",
        "pyyaml>=6.0",
        "jsonschema>=4.0.0",
        "pillow>=9.0.0",
        "opencv-python>=4.5.0",
        "librosa>=0.9.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "isort>=5.10.0",
            "flake8>=5.0.0",
        ],
        "research": [
            "jupyter>=1.0.0",
            "datasets>=2.0.0",
            "wandb>=0.13.0",
        ],
        "production": [
            "redis>=4.0.0",
            "celery>=5.2.0",
            "prometheus-client>=0.15.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "evalx=evalx.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords="llm evaluation metrics ai nlp machine-learning",
    include_package_data=True,
    package_data={
        "evalx": ["*.md", "*.yaml", "*.json"],
    },
    zip_safe=False,
) 