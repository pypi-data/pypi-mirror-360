from setuptools import setup, find_packages

setup(
    name="mirrorearth_sdk",
    version="0.1.0",
    author="MirrorEarth",
    author_email="info@mirrorearth.com",
    description="Python SDK for MirrorEarth Weather API",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://open.mirror-earth.com/docs/get-started/1-start",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy",
        "pandas",
        "flatbuffers",
        "requests"
        # Add any other dependencies your SDK requires
    ],
) 