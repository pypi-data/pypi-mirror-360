from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="aa-kit",
    version="0.1.0",
    author="Harsh Joshi",
    author_email="harsh.joshi.pth@gmail.com",
    description="The Universal AI Agent Framework - MCP-native, 3-line agent creation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/josharsh/aa-kit",
    project_urls={
        "Bug Tracker": "https://github.com/josharsh/aa-kit/issues",
        "Documentation": "https://aa-kit.dev/docs",
        "Source Code": "https://github.com/josharsh/aa-kit",
    },
    packages=find_packages(exclude=["tests*", "examples*", "docs*", "aa-kit-website*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "httpx>=0.25.0",
        "typing-extensions>=4.0.0",
        "python-dotenv>=1.0.0",
        "aiofiles>=23.0.0",  # For async file operations
    ],
    extras_require={
        "validation": ["pydantic>=2.6.0"],  # Optional validation with pydantic
        "openai": ["openai>=1.0.0"],
        "anthropic": ["anthropic>=0.7.0"],
        "redis": ["redis>=5.0.0"],
        "postgres": ["psycopg2-binary>=2.9.0"],
        "all": [
            "pydantic>=2.6.0",
            "openai>=1.0.0",
            "anthropic>=0.7.0",
            "redis>=5.0.0",
            "psycopg2-binary>=2.9.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "ruff>=0.1.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "aa-kit=aakit.cli:main",
        ],
    },
    keywords="ai agents mcp llm openai anthropic framework",
)