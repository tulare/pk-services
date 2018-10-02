# -*- encoding: utf-8 -*-

from setuptools import setup, find_packages

# Get version without import module
exec(compile(open('pk_services/version.py').read(),
             'pk_services/version.py', 'exec'))

install_requires = [
    # List your project dependencies here.
    # For more details, see:
    # https://setuptools.readthedocs.io/en/latest/setuptools.html#declaring-dependencies
    'youtube-dl>=2018.9',
]

with open('README.md') as f :
    readme = f.read()

with open('LICENSE') as f :
    license = f.read()

setup(
    name='pk-services',
    version=__version__,
    description='Various services for python projects',
    long_description=readme,
    author='Tulare Regnus',
    author_email='tulare.paxgalactica@gmail.com',
    url='https://github.com/tulare/pk-services',
    license=license,
    packages=find_packages(exclude=('tests',)),
    zip_safe=False,
    install_requires=install_requires
)
