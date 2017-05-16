#!/usr/bin/env python

from setuptools import setup


def read(path):
    with open(path) as f:
        return f.read()


setup(
    name='lollipop-hypothesis',
    version='0.2',
    description=('Library to generate random test data using Hypothesis '
                 'based on Lollipop schema'),
    long_description=read('README.rst'),
    author='Maxim Kulkin',
    author_email='maxim.kulkin@gmail.com',
    url='https://github.com/maximkulkin/lollipop-hypothesis',
    license='MIT',
    keywords=('lollipop', 'hypothesis'),
    packages=['lollipop_hypothesis'],
    install_requires=[
        'hypothesis>=3.8',
        'hypothesis[datetime]',
        'lollipop>=1.1.3',
        'six>=1.10',
    ],
    extras_require={
        'regex': ['hypothesis-regex'],
    },
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
)
