import os
from distutils.core import setup
from setuptools import find_packages


def read(fname):
    """Read the contents of a file"""
    return open(os.path.join(os.path.dirname(__file__), fname), 'r', encoding='utf-8').read()


# Read requirements from requirements.txt
with open('requirements.txt', 'r') as f:
    install_requires = []
    for line in f:
        req = line.strip()
        if req and not req.startswith('#'):
            install_requires.append(req)

# Find all packages
packages = find_packages()

# Get version from __init__.py
version = {}
with open("inspect4j/__init__.py") as fp:
    exec(fp.read(), version)

setup(
    name='inspect4j',
    version=version["__version__"],
    packages=packages,
    url='https://git.ecdf.ed.ac.uk/msc-24-25/inspect4j.git',
    license='MIT',
    author='Liru Qu', 
    description='Static code analysis tool for Java repositories',
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    include_package_data=True,
    install_requires=install_requires,
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Quality Assurance",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'inspect4j=inspect4j.main:main',
        ],
    },
    package_data={
        'inspect4j': [
            'licenses/*.txt',
        ],
    },
    zip_safe=False,
) 