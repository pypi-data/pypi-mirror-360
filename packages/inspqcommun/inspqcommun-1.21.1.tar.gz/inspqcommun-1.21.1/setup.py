#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import io
import os

from setuptools import setup, find_packages

def get_version():
    output_stream = os.popen('git describe')
    version = output_stream.read().strip()
    splitted_version = version.split('-')
    final_version = splitted_version[0]
    if len(splitted_version) > 1:
        final_version = "{version}.post{additionnal_commits}".format(
            version=splitted_version[0],
            additionnal_commits=splitted_version[1])
    return final_version

setup(
    # Needed to silence warnings (and to be a worthwhile package)
    name='inspqcommun',
    url='https://gitlab.forge.gouv.qc.ca/inspq/commun/python/inspqcommun.git',
    author='Philippe Gauthier',
    author_email='philippe.gauthier@inspq.qc.ca',
    # Needed to actually package something
    packages=find_packages(include=['inspqcommun*']),
    # Needed for dependencies
    install_requires=['fhirclient==1.0.3','wheel','urllib3','requests','pyjwt','jinja2','PyYAML','confluent_kafka','pygelf','six','str2bool','python-dateutil'],
    # *strongly* suggested for sharing
    version=get_version(),
    #version_command=('git describe', "pep440-git-local"),
    # The license can be anything you like
    license='LiLiQ',
    description='Librairies communes de INSPQ',
    long_description=io.open('README.md', 'r', encoding="utf-8").read(),
)
