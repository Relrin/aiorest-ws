# -*- coding: utf-8 -*-
import os
import re
import ast
from setuptools import setup, find_packages

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('aiorest_ws/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

requirements = ['autobahn>=0.12.0', ]
test_requirements = requirements + ['pytest', 'pytest-asyncio',
                                    'pytest-cov', 'pytest-xdist']


def read(f):
    return open(os.path.join(os.path.dirname(__file__), f)).read().strip()

args = dict(
    name='aiorest-ws',
    version=version,
    url='https://github.com/Relrin/aiorest-ws',
    license='BSD',
    author='Valeryi Savich',
    author_email='relrin78@gmail.com',
    description='REST framework with WebSockets support',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=requirements,
    tests_require=test_requirements,
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: WWW/HTTP'
    ],
)


if __name__ == '__main__':
    setup(**args)
