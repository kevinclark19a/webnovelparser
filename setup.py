#!/usr/bin/env python

from setuptools import setup, find_packages

if __name__ == '__main__':

    setup(
        name='webnovelparser',
        version='0.0.1',
        description='',

        python_requires='>=3.8',
        install_requires=['requests', 'bs4', 'setuptools', 'tenacity'],

        entry_points= {
            'console_scripts': ['webnovelparser=webnovelparser.cmdline:run']
        },

        packages=find_packages(),
        include_package_data=True
    )
