from setuptools import setup, find_packages

setup(
    name="actualcauses",
    version="0.2",
    packages=find_packages(),
    install_requires=[
        "tqdm>=4.62.3",
        "numpy>=1.21.0",
    ],
    author="SamuelReyd",
    author_email="samuelreyd@gmail.com",
    description="A package for Actual Causes Identification",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/SamuelReyd/ActualCausesIdentification",
)