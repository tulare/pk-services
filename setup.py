from setuptools import setup

def readme() :
    with open('README.md') as f :
        return f.read()

def license() :
    with open('LICENSE') as f:
        return f.read()

# Get version without import module
with open('src/pk_services/version.py') as f :
    exec(compile(f.read(), 'pk_services/version.py', 'exec'))

setup(
    name='pk-services',
    version=__version__,
    description='Various services for python projects',
    long_description=readme(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.11',
        'Topic :: Utilities :: Services',
    ],
    keywords='python service web',
    url='https://github.com/tulare/pk-services',
    author='Tulare Regnus',
    author_email='tulare.paxgalactica@gmail.com',
    license=license(),
    package_dir={'' : 'src'},
    packages=['pk_services'],
    package_data={'pk_services' : []},
    include_package_data=True,
    install_requires=[
        'PySocks>=1.7.1',
        'lxml>=4.9.3',
        'yt-dlp>=2023.9.24'
    ],
    scripts=[],
    entry_points={
        'console_scripts' : [],
    },
    data_files=[
    ],
    test_suite='nose2.collector.collector',
    tests_require=['nose2'],
    zip_safe=False
)


