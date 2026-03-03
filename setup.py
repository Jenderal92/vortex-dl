from setuptools import setup, find_packages

setup(
    name="vortex-dl",
    version="1.3.0",
    author="Smile Of Beauty",
    description="High-Performance Asynchronous Multi-part Downloader",
    long_description=open("README.md").read() if os.path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "httpx>=0.24.0",
        "rich>=13.0.0",
        "typer>=0.9.0",
        "packaging>=23.0",
    ],
    entry_points={
        "console_scripts": [
            "vortex-dl=vortex_dl.main:app",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)