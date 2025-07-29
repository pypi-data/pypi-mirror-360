# -*- coding: utf-8 -*-
# Copyright (C) 2012 Anaconda, Inc
# SPDX-License-Identifier: BSD-3-Clause

from setuptools import setup

setup(
    name='mergeLines',
    packages=['mergeLine'],
    description="merge lines after houghlinesp",
    version='2.0.1',
    long_description="""
demo:
import  mergeLine

mergeLine.merge_lines(  
        [1,0,0,1],
      [2,0,0,2],
      [3,0,0,3],  
)

    
    
    """,
    long_description_content_type= 'text/markdown',
)
