#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 30 07:53:09 2021

@author: benjamin
"""

from setuptools import setup, find_packages

setup(name='tauspeech',
      version='0.0.0',
      description='Tau analysis of speech articulatory movements',
      url='https://git.ecdf.ed.ac.uk/belie/tauspeech',
      author='Benjamin Elie',
      author_email='benjamin.elie@ed.ac.uk',
      license='Creative Commons Attribution 4.0 International License',
      packages=find_packages(),
      install_requires=[
        "numpy",
        "scipy",
        "pytest",
        "h5py",
        "joblib",
        "tqdm"
    ],      
      zip_safe=False)
