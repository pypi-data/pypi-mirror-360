from setuptools import setup, find_packages

setup(
    name="bruteforce-password",
    version="0.1.0",
    description="A tool to brute-force passwords (for educational purposes)",
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
