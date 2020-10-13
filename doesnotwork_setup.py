from os import path

from setuptools import find_packages, setup

from xmler import VERSION

cur_dir = path.abspath(path.dirname(__file__))

setup(
    name='xmler',
    version=VERSION,
    description='XMLer',
    install_requirements=[
        'click',
        'schwifty',
        'schema',
        'sepaxml',
        'tqdm',
        'unidecode',
    ],
    include_package_data=True,
    packages=find_packages('xmler'),
)
