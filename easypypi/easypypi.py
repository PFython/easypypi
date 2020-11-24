from pprint import pprint
import os
import datetime
import requests
import webbrowser
from cleverdict import CleverDict
import json
from pathlib import Path
from decimal import Decimal as decimal
import PySimpleGUI as sg

from classifiers import classifier_list
from licenses import licenses_dict
from shared_functions import create_file, update_line
from setup_template import HERE, PACKAGE_NAME, GITHUB_ID, VERSION, DESCRIPTION, LICENSE, AUTHOR, EMAIL, KEYWORDS, CLASSIFIERS, REQUIREMENTS, URL

def select_license():
    """
    Select from a shortlist of common license types
    """
    licenses = [CleverDict(x) for x in licenses_dict]
    layout = [[sg.Text(text=f"Please select a License for your package:")]]
    for license in licenses:
        layout.extend([[sg.Radio(license.key.upper(), "licenses", font="bold 12" ,tooltip = license.description, size = (10,1)), sg.Text(text=license.html_url, enable_events=True, size = (40,1))]])
    layout += [[sg.Button("OK"), sg.Button("Skip")]]
    window = sg.Window("easypypi", layout, size = (600,400),resizable=True)
    while True:
        event, values  =  window.read(close=True)
        if event == "OK" and any(values.values()):
            window.close()
            return [licenses[k] for k,v in values.items() if v][0]
        if event == "Skip" or not event:
            window.close()
            return
        if "http" in event:
            webbrowser.open(event)

def finalise_license(license):
    """ Make simple updates based on license.implementation instructions """
    year = str(datetime.datetime.now().year)
    replacements = dict()
    if license.key == 'lgpl-3.0':
        license.body += '\nThis license is an additional set of permissions to the <a href="/licenses/gpl-3.0">GNU GPLv3</a> license which is reproduced below:\n\n'
        gpl = [CleverDict(x) for x in licenses_dict if x['key'] == 'gpl-3.0'][0]
        license.body += gpl.body
    if license.key == "mit":
        replacements = {"[year]": year,
                        "[fullname]": AUTHOR}
    if license.key in ['gpl-3.0', 'lgpl-3.0', 'agpl-3.0']:
        replacements = {"<year>": year,
                        "<name of author>": AUTHOR,
                        "<program>": PACKAGE_NAME,
                        "Also add information on how to contact you by electronic and paper mail.": f"    Contact email: {EMAIL}",
                        "<one line to give the program's name and a brief idea of what it does.>": f"{PACKAGE_NAME}: {DESCRIPTION}"}
    if license.key == "apache-2.0":
        replacements = {"[yyyy]": year,
                        "[name of copyright owner]": AUTHOR}
    if replacements:
        for old, new in replacements.items():
            license.body = license.body.replace(old, new)
    return license

def get_next_version_number():
    """ Simple rules for suggesting next package version number """
    global VERSION
    decimal_version = decimal(str(VERSION))
    try:
        _, digits, exponent =decimal_version.as_tuple()
        if exponent == 0:  # i.e. 0 decimal places:
            increment = "0.1"
        else:
            increment = "0.01"
        return str(decimal_version + decimal(increment))
    except dec.InvalidOperation:
        return new_version+"-new"
    # TODO: Offer other schemas e.g. date format 2020.21.11

def input(text, default, old_line_starts):
    """
    Prompts for new values with PySimpleGui and returns a new line to update
    the old line in setup.py
    """
    key = old_line_starts.split()[0]
    if default == get_default_value:
        default = get_default_value(key)
    new = sg.popup_get_text(text, title="easypypi", default_text = default)
    globals()[key] = new
    return new

def get_default_value(key):
    """
    Just-in-time creation of suggested default, updated based on previous input
    """
    return {"URL": f"https://github.com/{GITHUB_ID}/{PACKAGE_NAME}",
            "KEYWORDS": f"{PACKAGE_NAME}, {AUTHOR}, {GITHUB_ID}, ",}[key]


def create_choice_box(group,choices):
    """
    Creates a scrollable checkbox popup using PySimpleGui
    Returns a list of selected choices, or and empty list
    """
    prompt = [sg.Text(text=f"Please select any relevant classifiers in the {group.title()} group:")]
    layout = [[sg.Checkbox(text=choice)] for choice in choices]
    buttons = [sg.Button("OK"), sg.Button("Skip")]
    event, checked  =  sg.Window("easypypi", [prompt,[sg.Column(layout, scrollable=True, vertical_scroll_only=True, size= (600,300))], buttons], size= (600,400),resizable=True).read(close=True)
    if event == "OK":
        return [choices[k] for k,v in checked.items() if v]
    else:
        return []

def get_classifiers():
    """
    Selects classifiers in key categories to better describe the package
    """
    global CLASSIFIERS
    if CLASSIFIERS == "":
        CLASSIFIERS = []
    for group in "Development Status|Intended Audience|Operating System|Programming Language :: Python|Topic".split("|"):
        choices = [x for x in classifier_list if x.startswith(group)]
        CLASSIFIERS.extend(create_choice_box(group, choices))
    CLASSIFIERS = ", ".join(CLASSIFIERS)


def create_new_script():
    """ Prompts for package metadata to be compiled into setup.py """
    data = {"PACKAGE_NAME": ["Please enter a name for this package:",
                     "mycleverpackage",
                     "PACKAGE_NAME = "],
            "VERSION": ["Please enter latest version number:",
                        get_next_version_number(),
                        "VERSION = "],
            "GITHUB_ID": ["Please enter your Github ID:",
                          "",
                          "GITHUB_ID = "],
            "URL": ["Please enter a link to the package repository:",
                    get_default_value,
                    "URL = "],
            "DESCRIPTION": ["Please enter a description:",
                          "",
                          "DESCRIPTION = "],
            "AUTHOR": ["Please the full name of the author:",
                       "",
                       "AUTHOR = "],
            "EMAIL": ["Please enter an email address for the author:",
                      "",
                      "EMAIL = "],
            "KEYWORDS": ["Please enter some keywords separated by a comma:",
                         get_default_value,
                         "KEYWORDS = "],
            "REQUIREMENTS": ["Please enter any packages/modules that absolutely need to be installed for yours to work, separated by commas:",
                             "cleverdict, ",
                             "REQUIREMENTS = "],}

    global SCRIPT, CLASSIFIERS, LICENSE
    for key, values in data.items():
        if not globals()[key]:  # variable is empty
            new_value = input(*values)
            SCRIPT = update_line(SCRIPT, values[2], new_value)
    if not CLASSIFIERS:
        get_classifiers()  # Checkbox input not text
        SCRIPT = update_line(SCRIPT, "CLASSIFIERS = ", str(CLASSIFIERS))
    if not LICENSE:
        LICENSE = select_license()
        if LICENSE:
            LICENSE = finalise_license(LICENSE)
        SCRIPT = update_line(SCRIPT, "LICENSE = ", LICENSE.name)

def run_shell_script():

    # Update VERSION (above) then run the following from the command prompt:

    print("> Installing setuptools and twine if not already present...")
    os.system('cmd /c "python -m pip install setuptools wheel twine"')

    print("> Running setup.py...")
    os.system('cmd /c "python -m pip install setuptools wheel twine"')

    #
    # python setup.py sdist
    # python -m twine upload --repository testpypi dist/*

    # Then:
    # pip install -i https://test.pypi.org/simple/ AWSOM

    # And when you're ready to go fully public:
    # python -m twine upload --repository pypi dist/*

def create_folder_structure():
    """
    Creates skeleton folder structure for a package and starter files.
    Returns the new directory path of the package.
    """
    package_path = Path(sg.popup_get_folder("Please select the parent folder for your package i.e. without the package name")) / PACKAGE_NAME
    # TODO: Create folders and files
    for path in (package_path, package_path / PACKAGE_NAME):
        try:
            os.mkdir(path)
            print(f"Created package folder {path}")
        except FileExistsError:
            print(f"Folder already exists {path}")
    return package_path

def create_essential_files(path):
    """
    Creates essential files for the new package:
    /setup.py
    /README.md
    /LICENSE
    /PACKAGE_NAME/__init__.py
    /PACKAGE_NAME/PACKAGE_NAME.py
    /PACKAGE_NAME/test_PACKAGE_NAME.py
    """
    create_file(path / PACKAGE_NAME / "__init__.py", [f"from {PACKAGE_NAME} import *"])
    create_file(path / PACKAGE_NAME / (PACKAGE_NAME + ".py"), [f"# {PACKAGE_NAME} by {AUTHOR}\n\n", f"# {datetime.datetime.now()}\n\n"])
    create_file(path / PACKAGE_NAME / ("test_" +PACKAGE_NAME + ".py"), [f"# Tests for {PACKAGE_NAME}\n\n", "\n\n", f"from {PACKAGE_NAME} import *\n\n", "import pytest\n\n", "", "class Test_Group_1:\n\n", "    def test_something(self):\n\n", '        """ Something should happen when you run something() """\n\n', "        assert something() == something_else\n\n"])
    create_file(path / "setup.py", SCRIPT)
    create_file(path / "LICENSE", LICENSE.body)
    create_file (path / "README.md", [f"#{PACKAGE_NAME}\n\n", DESCRIPTION+"\n\n", "###OVERVIEW\n\n", "###INSTALLATION\n\n", "###BASIC USE\n\n", "###UNDER THE BONNET\n\n", "###CONTRIBUTING\n\n", f"Contact {AUTHOR} {EMAIL}\n\n", "###CREDITS\n\n"])

    # TODO: Import defaults from README_template, test_template, init_template
    # to enable easier editing/personalisation



if __name__ == "__main__":
    sg.change_look_and_feel('DarkAmber')
    print(f"setup_template.py located in {HERE}")
    global SCRIPT
    with open(HERE / "setup_template.py", "r") as file:
        SCRIPT = file.readlines()
    create_new_script()
    package_path = create_folder_structure()
    create_essential_files(package_path)
    run_shell_script()
    #TODO: Save persistent data e.g. AUTHOR and EMAIL, maybe as env. variables?


