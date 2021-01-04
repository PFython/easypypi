#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@created: 09.12.20
@author: felix
"""
from pathlib import Path

from PySimpleGUI.PySimpleGUI import ICON_BUY_ME_A_COFFEE

# Variable names used within setup_template.py to create easyPyPI setup.py files
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

# Main groups of Classifiers for setup.py;  Values are input prompts
GROUP_CLASSIFIERS = {
    'Development Status': 'Classifiers (Development Status):',
    'Intended Audience': 'Classifiers (Audience):',
    'Operating System': 'Classifiers (OS):',
    'Programming Language :: Python': 'Classifiers (Python Version):',
    'Topic': 'Classifiers (Topic):',
    'License :: OSI Approved ::': 'Classifiers (License):',
}

# Common replacements used to create final LICENSE text
REPLACEMENTS = [
    '{self.author}',
    '{self.description}',
    '{self.email}',
    '{self.name}',
    '{datetime.datetime.now()}',
]

# Global keyword arguments for PySimpleGUI popups:
SG_KWARGS = {
    "title": "easyPyPI",
    "keep_on_top": True,
    "icon": Path(__file__).parent.parent / "easypypi.ico",
}
