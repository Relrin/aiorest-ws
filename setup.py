import os
import re
import ast
import sys
from setuptools import setup

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('flask/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

requirements = ['aiohttp>=0.15.3', ]
if sys.version_info < (3, 4):
    requirements += ['asyncio', ]

tests_require = requirements + ['pytest', 'pytest-asyncio', 
                                'pytest-cov', 'pytest-xdist']

def read(f):
    return open(os.path.join(os.path.dirname(__file__), f)).read().strip()

args = dict(
    name='aiorest-ws',
    version=version,
    url='https://github.com/Relrin/aiorest-ws',
    license='MIT',
    author='Valeryi Savich',
    author_email='relrin78@gmail.com',
    description='REST framework with WebSockets support',
    long_description='\n\n'.join((read('README.md'),)),
    packages=['aiorest_ws', ],
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=requirements,
    tests_require=tests_require,
    # add there test_suite 
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: WWW/HTTP'
    ],
)

setup(**args)
