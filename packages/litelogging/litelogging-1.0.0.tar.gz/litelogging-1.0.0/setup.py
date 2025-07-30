from setuptools import setup, find_packages

setup(
    name='litelogging',  # Replace with your package’s name
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        # List your dependencies here
    ],
    author='Missclick',  
    author_email='gabrielgarronedev@gmail.com',
    description='A library for terminal logging with color support and debug information',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',  # License type
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',

)