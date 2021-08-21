import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name = 'remoshock',
    version = '0.5.0',
    author = 'Nils Winter',
    author_email = 'nils.winter@yahoo.com',
    classifiers = [
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: POSIX :: Linux',
    ],
    description = 'Computer based shock-collar remote control with "evil" features.',
    entry_points={
        'console_scripts': [
            'remoshockcli = remoshock.cli:main',
            'remoshockrnd = remoshock.randomizer:main',
            'remoshockserver = remoshock.server:main'
        ],
    },
#    install_requires=['numpy'],
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    license="GNU Affero General Public License v3 (AGPL)",
    license_files = ('docs/LICENSE.md'),
    package_data={
      '': ['*'],
    },
    package_dir={'': 'src'},
    packages=setuptools.find_namespace_packages(where='src'),
    python_requires = '>=3.6',
    url = 'https://github.com/remoshock/remoshock',
)