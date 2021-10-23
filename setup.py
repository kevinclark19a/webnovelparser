#!/usr/bin/env python

from setuptools import setup, find_packages

def get_package_list(root_dir, package_name):
    return [ package_name ] + [ f'{package_name}.{pkg}' for pkg in find_packages(root_dir) ]

if __name__ == '__main__':

    root_pkg_dir = 'src'
    base_pkg_name = 'webtoepub'

    setup(
        name='webtoepub',
        version='0.0.1',
        description='',

        python_requires='>=3.6',
        install_requires=['requests', 'bs4', 'setuptools'],

        entry_points= {
            'console_scripts': ['webtoepub=webtoepub.cmdline.main:run']
        },

        include_package_data=True,
        packages=get_package_list(root_pkg_dir, base_pkg_name),
        package_dir={
            base_pkg_name: root_pkg_dir
        }
    )