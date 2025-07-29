from setuptools import setup, find_packages

setup(
    name="safe_import",
    version="0.1.0",
    description="Auto-install missing Python modules at import time",
    packages=find_packages(),
    python_requires=">=3.6",
)
