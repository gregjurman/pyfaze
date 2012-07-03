from setuptools import setup, find_packages
import sys, os

version = '0.1.2'

setup(name='pyfaze',
    version=version,
    description="Communication library for Anafaze/Watlow thermal controllers",
    long_description="""\
    """,
    classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='anafaze watlow serial temp industrial',
    author='Greg Jurman',
    author_email='gdj2214@rit.edu',
    url='https://github.com/gregjurman/pyfaze',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    test_suite = 'nose.collector',
    tests_require = [
        'nose',
        'mock'
    ],
    install_requires=[
    # -*- Extra requirements: -*-
        "pyserial"
    ],
    entry_points="""
    # -*- Entry points: -*-
    """,
)
