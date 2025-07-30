from setuptools import setup, find_packages
from pathlib import Path


# Read the README for long_description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="bruteforce-password",
    version="0.1.1",
    description="A tool to brute-force passwords (for educational purposes)",
    long_description=long_description,
    long_description_content_type="text/markdown",  # Tell PyPI it's Markdown
    author="Mustafa Qazi",
    author_email="mustafaqazi1998@gmail.com",
    packages=find_packages(),  # Automatically find all packages
    install_requires=[
        "tqdm"
    ],       # Add any dependencies here
    entry_points={
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.7",
    license="MIT"
)
