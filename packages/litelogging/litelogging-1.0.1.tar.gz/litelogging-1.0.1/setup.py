from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='litelogging',
    version='1.0.1',
    packages=find_packages(),
    install_requires=[
        # List your dependencies here
    ],
    author='Missclick',  
    author_email='gabrielgarronedev@gmail.com',
    description='A library for terminal logging with color support and debug information',
    long_description=long_description,
    long_description_content_type='text/markdown',  # Specify content type (if using .md)
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)