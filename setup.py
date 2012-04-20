from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='pyfaze',
      version=version,
      description="Communication library for Anafaze/Watlow thermal controllers",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='anafaze serial temp industrial',
      author='Greg Jurman',
      author_email='gdj2214@rit.edu',
      url='https://github.com/gregjurman/pyfaze',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
