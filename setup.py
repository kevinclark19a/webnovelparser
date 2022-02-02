#!/usr/bin/env python

from setuptools import setup, find_packages

if __name__ == '__main__':

    setup(
        name='webtoepub',
        version='0.0.1',
        description='',

        python_requires='>=3.6',
        install_requires=['requests', 'bs4', 'setuptools'],

        entry_points= {
            'console_scripts': ['webtoepub=webtoepub.cmdline.main:run']
        },

        packages=find_packages(),
        include_package_data=True
    )