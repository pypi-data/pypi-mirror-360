from setuptools import setup,find_packages
import shutil
import json

setup(
    name="ezcmt",
    version="0.1.12",
    packages=find_packages(),
    entry_points={
        "console_scripts":[
            "ezcmt=cli_tool.main:main"
        ]
    },
    install_requires=[
        "setuptools"
    ],
    author="mmemoo",
    description="A CLI tool for commiting in Git.",
    python_requires=">=3.10",
    include_package_data=True
)