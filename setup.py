import os
from setuptools import setup, find_packages


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="vortex-dl",
    version="1.0.0",
    author="Smile Of Beauty",
    author_email="Jenderal1337@gmail.com",
    description="🌀 Ultra-fast Asynchronous Multi-part CLI Downloader",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Jenderal92/vortex-dl",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "httpx>=0.27.0",
        "rich>=13.7.0",
        "typer>=0.9.0",
        "shellingham>=1.5.0", 
        "packaging>=23.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Utilities",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "vortex-dl=vortex_dl.main:app",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/Jenderal92/vortex-dl/issues",
        "Source": "https://github.com/Jenderal92/vortex-dl",
    },

)
