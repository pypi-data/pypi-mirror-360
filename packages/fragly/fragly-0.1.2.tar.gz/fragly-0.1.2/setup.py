from setuptools import setup, find_packages

setup(
    name="fragly",
    version="0.1.2",
    description="Async Python client for your FraglyFragment API service",
    author="Andrey",
    packages=find_packages(),
    install_requires=[
        "aiohttp>=3.9.0",
    ],
    python_requires=">=3.9",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
    ],
)