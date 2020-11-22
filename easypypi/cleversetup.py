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
from licenses import licenses_json
from helpers import create_file, replace
from setup_template import HERE, NAME, GITHUB_ID, VERSION, DESCRIPTION, LICENSE, AUTHOR, EMAIL, KEYWORDS, CLASSIFIERS, REQUIREMENTS, URL

def select_license():
    """
    Select from a shortlist of common license types
    """
    licenses = [CleverDict(x) for x in licenses_json]
    layout = [[sg.Text(text=f"Please select a License for your package:")]]
    for license in licenses:
        layout.extend([[sg.Radio(license.key.upper(), "licenses", font="bold 12" ,tooltip = license.description, size = (10,1)), sg.Text(text=license.html_url, enable_events=True, size = (40,1))]])
    layout += [[sg.Button("OK"), sg.Button("Skip")]]
    window = sg.Window("easypypi", layout, size = (600,400),resizable=True)
    while True:
        event, values  =  window.read(close=True)
        if event == "OK" and any(values.values()):
            window.close()
            break
        if event == "Skip" or not event:
            window.close()
            return []
        if "http" in event:
            webbrowser.open(event)
    # TODO: Auto update data.body e.g. with [year] and [fullname] for MIT

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
    Prompts for new values with PySimpleGui and returns a new line to replace
    the old line in setup.py
    """
    key = old_line_starts.split()[0]
    if default == get_latest_value:
        print("generating...")
        default = get_latest_value(key)
    new = sg.popup_get_text(text, title="easypypi", default_text = default)
    globals()[key] = new
    return f'{old_line_starts}"{new}"\n'

def get_latest_value(key):
    """
    Just-in-time creation of suggested default, updated based on previous input
    """
    return {"URL": f"https://github.com/{GITHUB_ID}/{NAME}",
            "KEYWORDS": f"{NAME}, {AUTHOR}, {GITHUB_ID}, ",
            "AUTHOR":  f"{GITHUB_ID.title()}",}[key]


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
    for group in "Development Status|Intended Audience|Operating System|Programming Language :: Python|Topic".split("|"):
        choices = [x for x in classifier_list if x.startswith(group)]
        CLASSIFIERS.extend(create_choice_box(group, choices))


def create_new_script():
    """ Prompts for package metadata to be compiled into setup.py """
    data = {"NAME": ["Please enter a name for this package:",
                     "mycleverpackage",
                     "NAME = "],
            "VERSION": ["Please enter latest version number:",
                        get_next_version_number(),
                        "VERSION = "],
            "GITHUB_ID": ["Please enter your Github ID:",
                          "",
                          "GITHUB_ID = "],
            "URL": ["Please enter a link to the package repository:",
                    get_latest_value,
                    "URL = "],
            "DESCRIPTION": ["Please enter a description:",
                          "",
                          "DESCRIPTION = "],
            "AUTHOR": ["Please the name of the author:",
                       get_latest_value,
                       "AUTHOR = "],
            "EMAIL": ["Please enter an email address for the author:",
                      "",
                      "EMAIL = "],
            "KEYWORDS": ["Please enter some keywords separated by a comma:",
                         get_latest_value,
                         "KEYWORDS = "],
            "REQUIREMENTS": ["Please enter any packages/modules that absolutely need to be installed for yours to work, separated by commas:",
                             "cleverdict, ",
                             "REQUIREMENTS = "],}

    for key, values in data.items():
        if not globals()[key]:  # variable is empty
            new_line = input(*values)
            SCRIPT = replace(SCRIPT, values[2], new_line)
            print("SCRIPT:",len(SCRIPT))

    CLASSIFIERS = get_classifiers()  # Checkbox input not text
    SCRIPT = replace(SCRIPT, "CLASSIFIERS = ", CLASSIFIERS)  # updates SCRIPT in place

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
    package_path = Path(sg.popup_get_folder("Please select the parent folder for your package i.e. without the package name")) / NAME
    # TODO: Create folders and files
    try:
        os.mkdir(package_path)
        print(f"Created package folder {package_path}")
    except FileExistsError:
        pass
    return package_path

def create_essential_files(path):
    """
    Creates essential files for the new package:
    /setup.py
    /README.md
    /LICENSE
    /NAME/__init__.py
    /NAME/NAME.py
    /NAME/test_NAME.py
    """
    create_file(path / "__init__.py", [f"from {NAME} import *"])
    # TODO: Import script_template
    create_file(path / (NAME + ".py"), [f"# {NAME} by {AUTHOR}", f"# {datetime.datetime.now()}"])
    # TODO: Import test_template
    create_file(path / ("test_" +NAME + ".py"), [f"# Tests for {NAME}", "", f"from {NAME} import *", "import pytest", "", "class Test_Group_1:", "    def test_something(self):", '        """ Something should happen when you run something() """', "        assert something() == something_else"])
    create_file(path.parent / "setup.py", SCRIPT)
    # TODO: Import readme_template.md
    create_file (path.parent / "README.md", [f"#{NAME}", DESCRIPTION, "###OVERVIEW", "###INSTALLATION", "###BASIC USE", "###UNDER THE BONNET", "###CONTRIBUTING", f"Contact {AUTHOR} {EMAIL}", "###CREDITS"])
    # TODO: Import LICENSE from Github:
    # https://developer.github.com/v3/licenses/
    create_file (path.parent / "LICENSE", ["Create a license here..."])



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
    #TODO: Save persistent data e.g. NAME and EMAIL, maybe as env. variables?


