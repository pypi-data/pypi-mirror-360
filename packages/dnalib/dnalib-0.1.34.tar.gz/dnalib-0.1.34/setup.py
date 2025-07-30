from setuptools import setup, find_packages

# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.rst").read_text(encoding='UTF-8')

setup(
    name='dnalib',
    version='0.1.34',    
    description='A Python library for fast development of Data Engineering ETL using spark.',    
    author='Charles Gobber',
    author_email='charles26f@gmail.com',
    license='Apache-2',
    packages=find_packages(),
    install_requires=['pyyaml==6.0.2', 'firebase-admin==6.6.0', 'pysftp==0.2.9', 'great_expectations==0.18.21'],
    long_description=long_description,
    long_description_content_type="text/markdown",
)