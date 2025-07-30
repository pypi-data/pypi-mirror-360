import os
import re
from setuptools import setup, find_packages

def read_meta():
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, "aipmodel", "__init__.py"), "r", encoding="utf-8") as f:
        content = f.read()

    version_match = re.search(r'__version__\s*=\s*"(.+?)"', content)
    desc_match = re.search(r'__description__\s*=\s*"(.+?)"', content)

    version = version_match.group(1) if version_match else None
    description = desc_match.group(1) if desc_match else None
    return version, description

version, description = read_meta()

setup(
    name="aipmodel",
    version=version,
    description=description,
    author="AIP MLOPS Team",
    author_email="mohmmadweb@gmail.com",
    url="https://github.com/AIP-MLOPS/model-registry",
    packages=find_packages(),
    install_requires=[],
    python_requires=">=3.6",
)