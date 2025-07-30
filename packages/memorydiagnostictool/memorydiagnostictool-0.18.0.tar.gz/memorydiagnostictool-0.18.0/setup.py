from setuptools import setup, find_packages

setup(
    name="memorydiagnostictool",
    version="0.18.0",
    packages=find_packages(),
    install_requires=[# List your dependencies here
    ],
    author="Tan Sau Kae",
    description="Memory Diagnostic Tool",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://confluence.amd.com/pages/viewpage.action?pageId=1673447643",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    license="MIT",
)
