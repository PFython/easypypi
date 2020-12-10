#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@created: 09.12.20
@author: felix
"""

SETUP_FIELDS = [
    'name',
    'version',
    'github_username',
    'url',
    'description',
    'author',
    'email',
    'keywords',
    'requirements',
    'license',
    'classifiers',
]

GROUP_CLASSIFIERS = [
    'Development Status',
    'Intended Audience',
    'Operating System',
    'Programming Language :: Python',
    'Topic',
]

REPLACEMENTS = [
    '{self.name}',
    '{self.description}',
    '{self.author}',
    '{self.email}',
    '{datetime.datetime.now()}',
]
