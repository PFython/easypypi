#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@created: 09.12.20
@author: felix
"""
from pathlib import Path

from PySimpleGUI.PySimpleGUI import ICON_BUY_ME_A_COFFEE

# Mapping of variable names used within setup_template.py and final setup.py,
# and Package attribute names.
SETUP_FIELDS = {
    "AUTHOR": "author",
    "CLASSIFIERS": "classifiers",
    "DESCRIPTION": "description",
    "EMAIL": "email",
    "GITHUB_USERNAME": "Github_username",
    "KEYWORDS": "keywords",
    "LICENSE": "license_name_github",
    "NAME": "name",
    "REQUIREMENTS": "requirements",
    "URL": "url",
    "VERSION": "version",
}

# Main groups of Classifiers for setup.py;  Values are input prompts
GROUP_CLASSIFIERS = {
    "Development Status": "Classifiers (Development Status):",
    "Intended Audience": "Classifiers (Audience):",
    "Operating System": "Classifiers (OS):",
    "Programming Language :: Python": "Classifiers (Python Version):",
    "Topic": "Classifiers (Topic):",
    "License :: OSI Approved ::": "Classifiers (License):",
}

# Common replacements used to create final LICENSE text
REPLACEMENTS = [
    "{self.author}",
    "{self.description}",
    "{self.email}",
    "{self.name}",
    "{self.Github_username}" "{datetime.datetime.now()}",
]

# Global keyword arguments for PySimpleGUI popups:
SG_KWARGS = {
    "title": "easyPyPI",
    "keep_on_top": True,
    "icon": Path(__file__).parent.parent / "easypypi.ico",
}
