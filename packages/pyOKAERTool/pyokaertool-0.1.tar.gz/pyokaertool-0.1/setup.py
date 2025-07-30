##################################################################
# setup.py for pyOKAERTool
from setuptools import setup, find_packages

setup(
    # Name and version of the package
    name='pyOKAERTool',
    version='0.1',
    packages=find_packages(),

    # List of package dependencies
    install_requires=[
        'numpy>=2.2.2',
    ],

    # Include additional files in the package
    include_package_data=True,
    package_data={
        '': ['*.py', '*.so'],
    },

    # Author and contact information
    author='Antonio Ríos-Navarro',
    author_email='arios@us.es',
    description='A Python package for AER Tool functionalities on a OpalKelly FPGA platform.',
)