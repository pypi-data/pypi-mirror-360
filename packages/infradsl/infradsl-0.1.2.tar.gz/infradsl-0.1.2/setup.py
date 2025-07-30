from setuptools import setup, find_packages
import os

# Get version from version file
def get_version():
    version_file = os.path.join(os.path.dirname(__file__), 'infradsl', '__version__.py')
    if os.path.exists(version_file):
        version_dict = {}
        with open(version_file, 'r') as f:
            exec(f.read(), version_dict)
            return version_dict['__version__']
    return "0.1.0"

# Get the long description from README.md
def get_long_description():
    readme_path = os.path.join(os.path.dirname(__file__), '..', 'README.md')
    try:
        with open(readme_path, "r", encoding="utf-8") as fh:
            return fh.read()
    except FileNotFoundError:
        return """
# InfraDSL - The Rails of Modern Infrastructure

InfraDSL brings Rails-like simplicity to cloud infrastructure management. Deploy production-ready applications to AWS, Google Cloud, and DigitalOcean with 95% less code than traditional tools.

## Quick Start

```python
# Deploy a web server in one line
server = AWS.EC2("web-server").t3_micro().ubuntu().service("nginx").create()

# Container app to Google Cloud Run
app = GoogleCloud.CloudRun("my-app").container("webapp", "./src").public().create()

# Complete production stack
database = AWS.RDS("app-db").postgresql().production().create()
storage = AWS.S3("app-assets").website().public().create()
api = AWS.ECS("app-api").fargate().container("api:latest").create()
```

Visit https://infradsl.dev for documentation and examples.
        """.strip()

setup(
    name="infradsl",
    version=get_version(),
    packages=find_packages(),
    
    # Dependencies
    install_requires=[
        # Core dependencies
        "click>=8.0.0",
        "python-dotenv>=1.0.0",
        "requests>=2.31.0",
        "pydantic>=2.0.0",
        "pyyaml>=6.0.0",
        "jinja2>=3.0.0",
        
        # DigitalOcean
        "pydo>=0.11.0",
        "python-digitalocean>=1.17.0",
        
        # Google Cloud
        "google-cloud-compute>=1.14.0",
        "google-cloud-storage>=2.10.0",
        "google-cloud-bigquery>=3.11.0",
        "google-cloud-functions>=1.16.0",
        "google-cloud-run>=0.10.0",
        "google-cloud-container>=2.22.0",
        "google-cloud-artifact-registry>=1.11.0",
        "google-api-python-client>=2.170.0",
        "google-auth>=2.23.0",
        
        # AWS
        "boto3>=1.34.0",
        "botocore>=1.34.0",
    ],
    
    # Optional dependencies for advanced features
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "docs": [
            "sphinx>=7.0.0",
            "sphinx-rtd-theme>=1.3.0",
        ],
        "all": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "sphinx>=7.0.0",
            "sphinx-rtd-theme>=1.3.0",
        ]
    },
    
    # CLI entry points
    entry_points={
        'console_scripts': [
            'infradsl=infradsl.cli:cli',
            'infra=infradsl.cli:cli',  # Short alias
        ],
    },
    
    # Include package data
    package_data={
        'infradsl': [
            'templates/**/*',
            'templates/**/**/*',
            '**/*.yaml',
            '**/*.yml',
            '**/*.json',
        ],
    },
    include_package_data=True,
    
    # Metadata
    author="InfraDSL Team",
    author_email="hello@infradsl.dev",
    description="Rails-like infrastructure management for AWS, Google Cloud, and DigitalOcean",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/infradsl/infradsl",
    project_urls={
        "Documentation": "https://infradsl.dev",
        "Bug Reports": "https://github.com/infradsl/infradsl/issues",
        "Source": "https://github.com/infradsl/infradsl",
        "Changelog": "https://github.com/infradsl/infradsl/blob/main/CHANGELOG.md",
    },
    
    # Classifiers for PyPI
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Systems Administration",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    
    # Keywords for discovery
    keywords="infrastructure cloud aws gcp digitalocean terraform pulumi iac devops rails",
    
    # Python version requirement
    python_requires=">=3.8",
    
    # License
    license="MIT",
    
    # Zip safe
    zip_safe=False,
)
