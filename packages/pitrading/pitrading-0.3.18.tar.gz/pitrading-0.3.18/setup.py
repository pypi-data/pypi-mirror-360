#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'redis',
    'pyzmq',
    'numpy',
    'pandas',
    'pytz',
    'pi_utils',
    'cos-python-sdk-v5',
    'scipy',
    'pdbpp',
 ]

test_requirements = [
    'redis',
    'pyzmq',
    'numpy',
    'pandas',
    'pytz',
    'pi_utils',
    'cos-python-sdk-v5',
    'scipy',
    'pdbpp',
]

setup(
    author="saaltfiish",
    author_email='hujiazhen@piasset.net',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Handy trading utils for PiAsset",
    entry_points={
        'console_scripts': [
            'pitrading=pitrading.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='pitrading',
    name='pitrading',
    packages=find_packages(include=['pitrading', 'pitrading.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://code.piasset.net/saaltfiish/pitrading',
    version='0.3.18',
    zip_safe=False,
)

# sudo apt install libjpeg8-dev zlib1g-dev
