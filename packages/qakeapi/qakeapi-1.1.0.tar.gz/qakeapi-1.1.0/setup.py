from setuptools import setup, find_packages

setup(
    name="qakeapi",
    version="1.1.0",
    description="A lightweight ASGI web framework for building fast web APIs with Python",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Aleksandr",
    author_email="fetis.dev@gmail.com",
    url="https://github.com/Craxti/qakeapi",
    packages=find_packages(),
    install_requires=[
        "uvicorn>=0.15.0",
        "pydantic>=2.0.0",
        "python-jose[cryptography]>=3.3.0",
        "passlib[bcrypt]>=1.7.4",
        "python-multipart>=0.0.5",
        "aiofiles>=0.8.0",
        "aiohttp>=3.8.0",
        "jinja2>=3.0.0",
        "psutil>=5.8.0",
    ],
    extras_require={
        "test": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.18.0",
            "pytest-cov>=3.0.0",
            "httpx>=0.25.0",
            "hypothesis>=6.75.0",
            "watchdog>=3.0.0",
            "memory-profiler>=0.61.0"
        ],
        "dev": [
            "black>=23.10.0",
            "isort>=5.12.0",
            "mypy>=1.6.0",
            "hypothesis>=6.75.0",
            "watchdog>=3.0.0",
            "memory-profiler>=0.61.0"
        ],
        "docs": [
            "mkdocs>=1.3.0",
            "mkdocs-material>=8.0.0",
        ],
    },
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: AsyncIO",
        "Intended Audience :: Developers",
        "Natural Language :: English",
    ],
    keywords="web framework api rest async asgi",
    project_urls={
        "Documentation": "https://github.com/Craxti/qakeapi/wiki",
        "Source": "https://github.com/Craxti/qakeapi",
        "Tracker": "https://github.com/Craxti/qakeapi/issues",
    },
) 