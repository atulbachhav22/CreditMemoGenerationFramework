from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="skill-engine",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A robust Python framework for executing LLM-orchestrated Skills defined in Markdown",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/skill-engine",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=[
        "pydantic>=2.5.0",
        "mistune>=3.0.0",
        "langchain>=0.1.0",
        "langchain-core>=0.1.0",
        "python-dotenv>=1.0.0",
        "rich>=13.0.0",
        "loguru>=0.7.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.7.0",
        ],
        "openai": ["langchain-openai>=0.0.2", "openai>=1.7.0"],
        "anthropic": ["langchain-anthropic>=0.1.0"],
        "pdf": ["pypdf2>=3.0.0"],
        "docs": ["python-docx>=1.1.0"],
    },
)
