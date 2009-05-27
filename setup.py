#from distutils.core import setup
from setuptools import setup
setup(name='telekommie',
    version='0.1',
    description='Telekommunisten Integration Environment',
    author='Dmytri Kleiner',
    author_email='dk@telekommunisten.net',
    url='http://cgit.telekommunisten.org/telekommie',
    test_suite='nose.collector',
    packages=['telekommie'],
)

