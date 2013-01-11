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
    description='Emitter for stream processing',
    url='http://github.com/brianhicks/emit',
    author='Brian Hicks',
    author_email='brian@brianthicks.com',
    license='MIT',
    packages=['emit'],
    scripts=['emit/bin/emit_digraph'],
    zip_safe=False
)
