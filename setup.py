from setuptools import setup
import os
from subprocess import Popen, PIPE
import sys

import emit


# add a few commands for measurement
def cc():
    proc = Popen(['radon', 'cc'] + sys.argv[1:], stdout=PIPE)
    stdout, _ = proc.communicate()
    sys.stdout.write(stdout.decode('utf-8'))
    return 1 if stdout else 0


def mi():
    proc = Popen(['radon', 'mi'] + sys.argv[1:], stdout=PIPE)
    stdout, _ = proc.communicate()
    sys.stdout.write(stdout.decode('utf-8'))
    for line in stdout.decode('utf-8').strip().split('\n'):
        if not line.endswith('A'):
            sys.stdout.write('One or more modules did not get an A. Failing.\n')
            return 1

    return 0


def read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except IOError:  # for tox
        return ''

if __name__ == '__main__':
    try:
        arg = sys.argv[1]
    except IndexError:
        arg = ''
    command = {'cc': cc, 'mi': mi}.get(arg, None)
    if command:
        sys.exit(command())

# pass execution to setuptools
setup(
    name='emit',
    version=emit.__version__,
    packages=['emit'],
    scripts=['emit/bin/emit_digraph'],

    # PyPI stuff
    author='Brian Hicks',
    author_email='brian@brianthicks.com',
    url='http://github.com/brianhicks/emit',
    description='Emitter for stream processing',
    keywords='stream processing',
    long_description=read('README.rst'),
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
