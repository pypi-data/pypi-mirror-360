"""
Setup configuration for hf-trainer-nbconvert package
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# Read requirements
requirements = (this_directory / "requirements.txt").read_text(encoding="utf-8").strip().split('\n')

setup(
    name="hf-trainer-nbconvert",
    version="1.0.1",
    author="K N S Sri Harshith",
    author_email="knssriharshith@gmail.com",
    description="Convert HuggingFace Trainer notebooks to HTML with preserved training data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/hf-trainer-nbconvert",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
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
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup :: HTML",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "hf-trainer-nbconvert=hf_trainer_nbconvert.cli:main",
        ],
    },
    keywords=[
        "jupyter", "notebook", "huggingface", "trainer", "machine-learning", 
        "html", "conversion", "nbconvert", "ml", "ai"
    ],
    project_urls={
        "Bug Reports": "https://github.com/knssriharshith/hf-trainer-nbconvert/issues",
        "Source": "https://github.com/knssriharshith/hf-trainer-nbconvert",
        "Documentation": "https://github.com/knssriharshith/hf-trainer-nbconvert#readme",
    },
)
