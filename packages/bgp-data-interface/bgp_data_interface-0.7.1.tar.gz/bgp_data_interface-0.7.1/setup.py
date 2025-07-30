from setuptools import setup, find_packages
import tomllib

with open("pyproject.toml", "rb") as file:
    data = tomllib.load(file)
    VERSION = data['project']['version']

setup(
    name='bgp_data_interface',
    version=VERSION,
    author='Anurat Chapanond',
    author_email='anurat.c@bgrimmpower.com',
    packages=find_packages(),
    scripts=[],
    url='http://pypi.python.org/pypi/bgp_data_interface/',
    license='LICENSE.txt',
    description='This is a python library for accessing internal and public data e.g. PI, AMR, openmeteo, etc.',
    long_description=open('README.md').read(),
    install_requires=[
        'pandas', 'numpy', 'requests', 'pytz', 'urllib3'
    ],
)
