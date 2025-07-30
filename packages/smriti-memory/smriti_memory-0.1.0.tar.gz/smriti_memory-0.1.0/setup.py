from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

setup(
    name="smriti-memory",
    version="0.1.0",
    author="Aman Kumar",
    author_email="ad721603@gmail.com",
    description="An intelligent memory layer for AI applications with RAG capabilities",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/amanyadav721/smriti",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pinecone-client>=2.0.0",
        "langchain>=0.3.0",
        "langchain-groq>=0.3.0",
        "langchain-google-genai>=2.0.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.0.0",
        "fastapi>=0.100.0",
        "uvicorn>=0.20.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
        ],
        "docs": [
            "sphinx>=6.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "smriti=smriti.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "smriti": ["py.typed"],
    },
    zip_safe=False,
) 