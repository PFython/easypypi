#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@created: 09.12.20
@author: felix
"""

SETUP_FIELDS = [
    'author',
    'classifiers',
    'description',
    'email',
    'github_username',
    'keywords',
    'license',
    'name',
    'requirements',
    'url',
    'version',
]

EASYPYPI_FIELDS = [
    'github_password',
    'license_text',
    'pypi_password',
    'pypi_test_password',
    'pypi_test_username',
    'pypi_username',
    'script_lines',
    'setup_filepath_str',
]

GROUP_CLASSIFIERS = [
    'Development Status',
    'Intended Audience',
    'Operating System',
    'Programming Language :: Python',
    'Topic',
]

REPLACEMENTS = [
    '{self.author}',
    '{self.description}',
    '{self.email}',
    '{self.name}',
    '{datetime.datetime.now()}',
]
