# setup.py
from setuptools import setup, find_packages

setup(
    name='jict_dict',
    version='0.1.1',
    description='Bidirectional dict with unhashable key/value support',
    author='ElJeiForeal',
    author_email='eljeiforeal@gmail.com',
    packages=find_packages(),
    python_requires='>=3.6',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
)
