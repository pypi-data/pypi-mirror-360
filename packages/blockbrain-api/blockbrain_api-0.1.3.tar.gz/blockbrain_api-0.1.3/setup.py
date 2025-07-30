import os

from setuptools import find_packages, setup


# Read the README file
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="blockbrain-api",
    version="0.1.0",
    author="BlockBrain",
    author_email="support@blockbrain.ai",
    description="A Python client for the BlockBrain API with simple chat, file upload, and streaming support",
    long_description=(
        read("README.md")
        if os.path.exists("README.md")
        else (
            "A modern Python client for the BlockBrain API with unified chat interface, "
            "file processing, and streaming support"
        )
    ),
    long_description_content_type="text/markdown",
    url="https://github.com/blockbrain/blockbrain-api-python",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
            "mypy",
        ],
    },
    entry_points={
        "console_scripts": [
            # You can add CLI commands here if needed
        ],
    },
    keywords="blockbrain api chat ai streaming nlp",
    project_urls={
        "Bug Reports": "https://github.com/blockbrain/blockbrain-api-python/issues",
        "Source": "https://github.com/blockbrain/blockbrain-api-python",
        "Documentation": "https://docs.blockbrain.ai",
    },
)
