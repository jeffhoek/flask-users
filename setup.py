#!/usr/bin/env python
__author__ = 'jeff'

from setuptools import find_packages, setup


def readme():
    with open('README.md') as f:
        return f.read()


def get_requirements():
    with open('requirements.txt') as r:
        reqs = r.read().split('\n')
    return reqs


setup(
    name='flask_users',
    version='0.1.0',
    packages=find_packages(),
    author_email='jeffreyscotthoekman@gmail.com',
    description='code challenge',
    long_description=readme(),
    install_requires=get_requirements()
)
