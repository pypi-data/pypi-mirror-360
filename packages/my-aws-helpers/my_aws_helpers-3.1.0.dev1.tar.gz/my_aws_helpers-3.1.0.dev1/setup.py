import os
from setuptools import find_namespace_packages, setup

base_path = os.path.abspath(os.path.dirname(__file__))

version = "3.1.0.dev1"

setup(
    name="my_aws_helpers",
    version=version,
    author="Jarrod McCarthy",
    description="AWS Helpers",
    url="https://github.com/JarrodMccarthy/aws_helpers.git",
    platforms="any",
    packages=[p for p in find_namespace_packages(where=base_path) if p.startswith("my_aws_helpers")],
    classifiers=[
        "License :: Other/Proprietary License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    zip_safe = True,
    install_requires = [
        "boto3==1.34.36"
    ],
    include_package_data=True,
)