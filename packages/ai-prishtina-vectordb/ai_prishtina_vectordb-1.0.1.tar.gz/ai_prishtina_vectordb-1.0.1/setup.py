from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="ai-prishtina-vectordb",
    version="1.0.1",
    author="Alban Maxhuni, PhD",
    author_email="info@albanmaxhuni.com",
    description="Enterprise-grade vector database library for AI applications with ChromaDB, multi-modal support, and cloud integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/albanmaxhuni/ai-prishtina-chromadb-client",
    project_urls={
        "Bug Reports": "https://github.com/albanmaxhuni/ai-prishtina-chromadb-client/issues",
        "Source": "https://github.com/albanmaxhuni/ai-prishtina-chromadb-client",
        "Documentation": "https://docs.ai-prishtina.com",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Database",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="vector database, chromadb, embeddings, semantic search, AI, machine learning, similarity search, document processing",
    python_requires=">=3.8",
    install_requires=[
        # Core dependencies
        "chromadb>=0.4.0",
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "scikit-learn>=1.0.0",
        "sentence-transformers>=2.2.2",
        "pydantic>=1.10.0,<2.0.0",
        "requests>=2.26.0",
        "python-dotenv>=0.19.0",
        "tqdm>=4.65.0",
        # Async support
        "aiofiles>=23.0.0",
        "aiohttp>=3.8.0",
        # File format support
        "openpyxl>=3.0.0",
        "python-docx>=0.8.11",
        "pypdf>=3.0.0",
        "Pillow>=8.0.0",
    ],
    extras_require={
        "full": [
            # All optional dependencies
            "torch>=1.9.0",
            "transformers>=4.11.0",
            "opencv-python>=4.10.0",
            "boto3>=1.26.0",
            "google-cloud-storage>=2.0.0",
            "azure-storage-blob>=12.0.0",
            "minio>=7.2.0",
            "redis>=4.0.0",
            "soundfile>=0.13.1",
            "docker>=6.0.0",
        ],
        "cloud": [
            "boto3>=1.26.0",
            "google-cloud-storage>=2.0.0",
            "azure-storage-blob>=12.0.0",
            "minio>=7.2.0",
        ],
        "ml": [
            "torch>=1.9.0",
            "transformers>=4.11.0",
            "opencv-python>=4.10.0",
            "soundfile>=0.13.1",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.10.0",
            "black>=23.0.0",
            "isort>=5.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "docs": [
            "sphinx>=7.0.0",
            "sphinx-rtd-theme>=1.3.0",
            "myst-parser>=2.0.0",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)