from setuptools import setup, find_packages
import os

# Read README.md with UTF-8 encoding
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except UnicodeDecodeError:
    # Fallback to system default encoding if UTF-8 fails
    with open("README.md", "r") as fh:
        long_description = fh.read()

# get required lib
with open("script/requirements.txt", "r") as file:
    requirements = file.read().strip().split("\n")

setup(
    name="infra_analytics",
    version="0.1.2",
    author="hautx2",
    author_email="hautx2@fpt.com",
    description="Sort description",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    # packages=find_packages(),
    packages=find_packages(include=["infra_analytics", "infra_analytics.*"]),
    # package_data={
    #     "infra_analytics": ["config.yaml"],
    # },
    include_package_data=True,
    # requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
