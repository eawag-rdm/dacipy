# _*_ coding: utf-8 _*_

from setuptools import setup, find_packages
setup(
    name = 'dacipy',
    version = '0.1',
    packages = find_packages(),
    install_requires = ['requests>=2.18.4'],
    author = 'Harald von Waldow',
    author_email = 'harald.vonwaldow@eawag.ch',
    description = ("Python implementation with CLI script of the"
                   " DataCite Metadata-Store API"
                   " (https://support.datacite.org/v1.1/reference#overview)"),
    license = " GNU AFFERO GENERAL PUBLIC LICENSE",
    keywords = 'datacite mds api',
    entry_points = {
        'console_scripts':
        ['scriptname=daciapi.daciapi:main']
    }
)
