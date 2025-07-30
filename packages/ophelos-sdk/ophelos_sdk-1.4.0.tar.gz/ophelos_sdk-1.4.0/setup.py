from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="ophelos-sdk",
    version="1.4.0",
    author="Ophelos",
    author_email="support@ophelos.com",
    description="Python SDK for the Ophelos API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tomasz-oph/ophelos_python_sdk",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Financial",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    license="MIT",
    keywords=["ophelos", "api", "sdk", "debt", "management", "payments", "collections"],
    project_urls={
        "Homepage": "https://github.com/tomasz-oph/ophelos_python_sdk",
        "Documentation": "https://github.com/tomasz-oph/ophelos_python_sdk",
        "Repository": "https://github.com/tomasz-oph/ophelos_python_sdk",
        "Bug Reports": "https://github.com/tomasz-oph/ophelos_python_sdk/issues",
        "Changelog": "https://github.com/tomasz-oph/ophelos_python_sdk/blob/main/CHANGELOG.md",
    },
)
