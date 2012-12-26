from setuptools import setup
import emit

setup(
    name='emit',
    version=emit.__version__,
    description='Emitter for celery tasks',
    url='http://github.com/brianhicks/emit',
    author='Brian Hicks',
    author_email='brian@brianthicks.com',
    license='MIT',
    packages=['emit'],
    zip_safe=False
)
