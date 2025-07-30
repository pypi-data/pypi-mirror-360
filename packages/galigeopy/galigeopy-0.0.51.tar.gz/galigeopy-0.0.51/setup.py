from pathlib import Path

import setuptools

VERSION = "0.0.51"  # PEP-440

NAME = "galigeopy"

INSTALL_REQUIRES = [
]


setuptools.setup(
    name=NAME,
    version=VERSION,
    description="Galigeo Python SDK",
    url="https://github.com/JPTGGO/galigeopy",
    project_urls={
        "Source Code": "https://github.com/JPTGGO/galigeopy",
    },
    author="Jules Pierrat",
    author_email="jpierrat@galigeo.com",
    license="Apache License 2.0",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.10",
    ],
    # Snowpark requires Python 3.8
    python_requires=">=3.8",
    # Requirements
    install_requires=INSTALL_REQUIRES,
    packages=setuptools.find_packages(exclude=["tests"]),
    long_description=Path("README.md").read_text(),
    long_description_content_type="text/markdown",
)