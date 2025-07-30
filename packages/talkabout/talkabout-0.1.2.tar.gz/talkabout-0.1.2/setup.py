"""
Setup configuration for the talkabout package.
"""

from setuptools import setup, find_packages

setup(
    name="talkabout",
    version="0.1.2",
    author="Denis Babochenko",
    description="AI-powered object query proxy using Claude AI",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/babochenko/talkabout",
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
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "anthropic>=0.18.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.900",
        ]
    }
)