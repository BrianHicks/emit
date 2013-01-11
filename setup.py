from setuptools import setup
import os
import emit

setup(
    name='emit',
    version=emit.__version__,
    description='Emitter for stream processing',
    url='http://github.com/brianhicks/emit',
    author='Brian Hicks',
    author_email='brian@brianthicks.com',
    license='MIT',
    packages=['emit'],
    scripts=['emit/bin/emit_digraph'],
    zip_safe=False
)
