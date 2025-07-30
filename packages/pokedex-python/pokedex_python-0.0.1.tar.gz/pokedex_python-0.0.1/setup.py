from setuptools import setup, find_packages
from os import path
working_directory = path.abspath(path.dirname(__file__))

with open(path.join(working_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pokedex_python', # name of packe which will be package dir below project
    version='0.0.1',
    url='https://github.com/Ishan-Karpe/Pokedex',
    author='Ishan Karpe',
    author_email='ishan.k.abhijeet@gmail.com',
    description='Simple Pokédex application in Python',
    long_description='' + long_description,
    packages=find_packages(), # Automatically find packages in the current directory
    install_requires=[],
)