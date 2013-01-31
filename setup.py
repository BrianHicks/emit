import distribute_setup
distribute_setup.use_setuptools()

import os
from setuptools import setup, find_packages

import emit

def read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except IOError:  # for tox
        return ''

setup(
    # System information
    name='emit',
    version=emit.__version__,
    packages=find_packages(exclude=('test',)),
    scripts=['emit/bin/emit_digraph'],
    zip_safe=True,
    extras_require = {
        'celery-routing': ['celery>=3.0.13'],
        'rq-routing': ['rq>=0.3.4', 'redis>=2.7.2'],
    },

    # Human information
    author='Brian Hicks',
    author_email='brian@brianthicks.com',
    url='https://github.com/brianhicks/emit',
    description='Build a graph to process streams',
    keywords='stream processing',
    long_description=read('README.rst')
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
