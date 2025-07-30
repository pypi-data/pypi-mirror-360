from setuptools import setup, find_packages
import os

# Read the README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Version
__version__ = "0.6.1"

setup(
    name="stocksblitz-shared",
    version="0.6.1",  # ✅ Fixed: Redis connection to use environment variables
    description="Shared Python library for StocksBlitz platform microservices",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Raghuram Mutya",
    author_email="raghu.mutya@gmail.com",
    url="https://github.com/raghurammutya/stocksblitz-platform",
    project_urls={
        "Bug Tracker": "https://github.com/raghurammutya/stocksblitz-platform/issues",
        "Documentation": "https://github.com/raghurammutya/stocksblitz-platform/tree/main/shared_architecture",
        "Source Code": "https://github.com/raghurammutya/stocksblitz-platform/tree/main/shared_architecture",
    },
    packages=find_packages(include=["shared_architecture", "shared_architecture.*"]),
    include_package_data=True,
    install_requires=[
        # Note: Most dependencies are provided by the base Docker image
        # Only include truly necessary runtime dependencies here
        "SQLAlchemy>=2.0.0",
        "pydantic>=2.0.0",
        "redis>=4.0.0",
        "fastapi>=0.100.0",
        "circuitbreaker>=1.3.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.0.0",
        ],
        "full": [
            "psycopg2-binary>=2.9",
            "asyncpg>=0.28.0",
            "aioredis>=2.0.0",
            "python-jose[cryptography]>=3.3.0",
            "passlib[bcrypt]>=1.7.4",
            "uvicorn>=0.20.0",
            "prometheus-fastapi-instrumentator>=6.0.0",
            "celery>=5.3.0",
        ],
    },
    python_requires=">=3.8",
    keywords="stocksblitz trading microservices shared library architecture",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Framework :: FastAPI",
        "Topic :: Office/Business :: Financial :: Investment",
    ],
)