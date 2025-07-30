'''
This setup.py file is used to package the mlslib library. It includes metadata such as the name, version, and author information.
The find_packages() function automatically discovers all packages and subpackages in the directory.
The install_requires list can be populated with any dependencies that the library requires.
The classifiers provide additional metadata about the package, such as the programming language version.
The URL field is optional and can point to the project's repository or documentation.
'''

from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='mlslib',
    version='0.1.11',
    packages=find_packages(),
    install_requires=['ipython>=7.0.0',  # For IPython.display.HTML
        'pyarrow>=6.0.0',
        'python-dateutil>=2.8.2'],
    description='A utility library for working with data pipelines on GCP',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Raj Jha',
    author_email='rjha4@wayfair.com',
    url='https://github.com/wayfair-sandbox/dslib',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
