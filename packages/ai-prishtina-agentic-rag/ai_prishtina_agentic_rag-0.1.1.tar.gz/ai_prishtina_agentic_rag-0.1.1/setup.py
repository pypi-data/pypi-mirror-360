"""Setup script for the Agentic RAG library."""

from setuptools import setup, find_packages

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ai-prishtina-agentic-rag",
    version="0.1.1",
    author="Alban Maxhuni, PhD",
    author_email="info@albanmaxhuni.com",
    description="A comprehensive, professional-grade agentic Retrieval-Augmented Generation (RAG) library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/ai-prishtina-agentic-rag",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.9",
    install_requires=[
        "pydantic>=2.0.0",
        "typing-extensions>=4.0.0",
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "openai>=1.0.0",
        "anthropic>=0.7.0",
        "cohere>=4.0.0",
        "transformers>=4.20.0",
        "torch>=1.12.0",
        "chromadb>=0.4.0",
        "pinecone-client>=2.2.0",
        "weaviate-client>=3.15.0",
        "faiss-cpu>=1.7.0",
        "langchain>=0.1.0",
        "pypdf>=3.0.0",
        "python-docx>=0.8.11",
        "beautifulsoup4>=4.11.0",
        "markdown>=3.4.0",
        "python-magic>=0.4.27",
        "spacy>=3.4.0",
        "nltk>=3.8.0",
        "sentence-transformers>=2.2.0",
        "tiktoken>=0.4.0",
        "requests>=2.28.0",
        "aiohttp>=3.8.0",
        "tenacity>=8.0.0",
        "rich>=12.0.0",
        "tqdm>=4.64.0",
        "pyyaml>=6.0",
        "python-dotenv>=0.19.0",
        "structlog>=22.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "isort>=5.10.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
            "pre-commit>=2.20.0",
        ],
        "docs": [
            "mkdocs>=1.4.0",
            "mkdocs-material>=8.5.0",
            "mkdocstrings[python]>=0.19.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ai-prishtina-agentic-rag=agentic_rag.cli:main",
        ],
    },
)
