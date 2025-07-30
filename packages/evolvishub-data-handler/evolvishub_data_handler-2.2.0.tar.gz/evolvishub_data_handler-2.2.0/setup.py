from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="evolvishub-data-handler",
    version="2.0.0",
    author="Alban Maxhuni, PhD",
    author_email="a.maxhuni@evolvis.ai",
    description="A Change Data Capture (CDC) library for data synchronization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/evolvishub/evolvishub-data-handler",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Database",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "sqlalchemy>=2.0.0",
        "psycopg2-binary>=2.9.0",
        "mysql-connector-python>=8.0.0",
        "pymssql>=2.2.0",
        "oracledb>=1.0.0",
        "pymongo>=4.0.0",
        "boto3>=1.26.0",
        "google-cloud-storage>=2.0.0",
        "azure-storage-blob>=12.0.0",
        "pandas>=2.0.0",
        "pyarrow>=12.0.0",
        "pydantic>=2.0.0",
        "pyyaml>=6.0.0",
        "python-dotenv>=1.0.0",
        "loguru>=0.7.0",
        "croniter>=1.3.0",
        "click>=8.0.0",
        "pytz>=2023.3",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.0.0",
            "mypy>=1.0.0",
            "flake8>=6.0.0",
            "pre-commit>=3.0.0",
        ],
        "docs": [
            "sphinx>=7.0.0",
            "sphinx-rtd-theme>=1.0.0",
            "sphinx-autodoc-typehints>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "evolvishub-cdc=evolvishub_data_handler.cli:main",
        ],
    },
) 