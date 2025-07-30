from setuptools import setup, find_packages
import os

def get_requirements():
    with open('requirements.txt') as f:
        return [line.strip() for line in f.readlines() if line.strip()]

setup(
    name="safeshield",
    version="1.6.0",
    packages=find_packages(),
    install_requires=get_requirements(),
    author="Wunsun Tarniho",
    author_email="wunsun58@gmail.com",
    description="Library for Help Validation Control",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/WunsunTarniho/py-guard",
    project_urls={
        "Bug Tracker": "https://github.com/WunsunTarniho/py-guard/issues",
    },
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Security",
    ],
    python_requires=">=3.10",
    include_package_data=True,
)