from pprint import pprint
from pathlib import Path
import os
import shutil
import click  # used to get cross-platform folder path for config file
import datetime
import requests
import webbrowser
from cleverdict import CleverDict
import json
from decimal import Decimal as decimal
import PySimpleGUI as sg

from classifiers import classifier_list
from licenses import licenses_dict
from shared_functions import create_file, update_line
from setup_template import HERE, PACKAGE_NAME, GITHUB_ID, VERSION, DESCRIPTION, LICENSE, AUTHOR, EMAIL, KEYWORDS, CLASSIFIERS, REQUIREMENTS, URL

SG_KWARGS = {"title": "easyPyPI", "keep_on_top": True}

# Persistent fields to keep in easyPyPI's config file:
CONFIG_FIELDS = "AUTHOR EMAIL GITHUB_ID TWINE_USERNAME TWINE_PASSWORD SCRIPT_PATH".split()
CONFIG = Path(click.get_app_dir("easyPyPI")) / ("config.json")
# os.remove(CONFIG)

def get_next_version_number():
    """ Suggests next package version number based on simple schemas """
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

def get_default_value(key):
    """
    Just-in-time generation of suggested default value after global variables
    (empty initially) are updated with user input.
    """
    return {"URL": f"https://github.com/{GITHUB_ID}/{PACKAGE_NAME}",
            "KEYWORDS": f"{PACKAGE_NAME}, {AUTHOR}, {GITHUB_ID}, ",}[key]

def prompt_with_textbox(text, default, old_line_starts):
    """
    Prompts for new values with PySimpleGui and returns a new line to update
    the old line in setup.py.  Also updates the global variable in place.
    """
    key = old_line_starts.split()[0]
    if default == get_default_value:
        default = get_default_value(key)
    new = sg.popup_get_text(text, default_text = default, **SG_KWARGS)
    globals()[key] = new
    return new

def prompt_with_checkboxes(group,choices):
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
        CLASSIFIERS.extend(prompt_with_checkboxes(group, choices))
    CLASSIFIERS = ", ".join(CLASSIFIERS)

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
            return licenses[0]  # Default license
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

def create_new_script():
    """
    Check global variables created from setup_template.py as well as the
    system environment variable EASYPIPY.  If no value is set, prompts for
    a value and updates SCRIPT, which will later be used to create setup.py
    """
    data = {"PACKAGE_NAME": ["Please enter a name for this package:",
                     "as_easy_as_pie",
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
                       get_config_value("AUTHOR"),
                       "AUTHOR = "],
            "EMAIL": ["Please enter an email address for the author:",
                      get_config_value("EMAIL"),
                      "EMAIL = "],
            "KEYWORDS": ["Please enter some keywords separated by a comma:",
                         get_default_value,
                         "KEYWORDS = "],
            "REQUIREMENTS": ["Please enter any packages/modules that absolutely need to be installed for yours to work, separated by commas:",
                             "cleverdict, ",
                             "REQUIREMENTS = "],}

    global SCRIPT
    for key, values in data.items():
        prompt, default_value, old_line_starts = values
        if default_value:
            globals()[key] = default_value
        else:
            default_value = get_config_value(key)
        new_value = prompt_with_textbox(prompt, default_value, old_line_starts)
        SCRIPT = update_line(SCRIPT, old_line_starts, new_value)
        if key in CONFIG_FIELDS:
            update_config_file()
    global CLASSIFIERS
    if not CLASSIFIERS:
        get_classifiers()  # Checkbox input not text
        SCRIPT = update_line(SCRIPT, "CLASSIFIERS = ", str(CLASSIFIERS))
    global LICENSE
    if not LICENSE:
        LICENSE = select_license()
        if LICENSE:
            LICENSE = finalise_license(LICENSE)
        SCRIPT = update_line(SCRIPT, "LICENSE = ", LICENSE.name)

def create_folder_structure():
    """
    Creates skeleton folder structure for a package and starter files.
    Updates global variable SCRIPT_PATH.
    """
    global SCRIPT_PATH
    SCRIPT_PATH  = Path(sg.popup_get_folder("Please select the parent folder for your package i.e. without the package name", default_path = SCRIPT_PATH, **SG_KWARGS))
    update_config_file()
    new_folder = SCRIPT_PATH / PACKAGE_NAME / PACKAGE_NAME
    try:
        os.makedirs(new_folder)
        print(f"Created package folder {new_folder}")
    except FileExistsError:
        print(f"Folder already exists {new_folder}")

def create_essential_files():
    """
    Creates essential files for the new package:
    /setup.py
    /README.md
    /LICENSE
    /PACKAGE_NAME/__init__.py
    /PACKAGE_NAME/PACKAGE_NAME.py
    /PACKAGE_NAME/test_PACKAGE_NAME.py
    """
    package_path = SCRIPT_PATH / PACKAGE_NAME
    create_file(package_path / PACKAGE_NAME / "__init__.py", [f"from {PACKAGE_NAME} import *"])
    create_file(package_path / PACKAGE_NAME / (PACKAGE_NAME + ".py"), [f"# {PACKAGE_NAME} by {AUTHOR}\n", f"# {datetime.datetime.now()}\n"])
    create_file(package_path / PACKAGE_NAME / ("test_" +PACKAGE_NAME + ".py"), [f"# Tests for {PACKAGE_NAME}\n", "\n", f"from {PACKAGE_NAME} import *\n", "import pytest\n", "", "class Test_Group_1:\n", "    def test_something(self):\n", '        """ Something should happen when you run something() """\n', "        assert something() == something_else\n"])
    create_file (package_path / "README.md", [f"# {PACKAGE_NAME}\n", DESCRIPTION+"\n\n", "### OVERVIEW\n\n", "### INSTALLATION\n\n", "### BASIC USE\n\n", "### UNDER THE BONNET\n\n", "### CONTRIBUTING\n\n", f"Contact {AUTHOR} {EMAIL}\n\n", "### CREDITS\n\n"])
    # setup.py and LICENSE should always be overwritten as most likely to
    # include changes from running easyPiPY.
    # The other files are just bare-bones initially, created as placeholders.
    create_file(package_path / "setup.py", SCRIPT, overwrite = True)
    create_file(package_path / "LICENSE", LICENSE.body, overwrite=True)

def copy_existing_files():
    """
    Prompts for additional files to copy over into the newly created folder:
    \PACKAGE_NAME\PACKAGE_NAME
    """
    files = sg.popup_get_file("Please select any other files to copy to new project folder", **SG_KWARGS, default_path="", multiple_files=True)
    for file in [Path(x) for x in files.split(";")]:
        new_file = SCRIPT_PATH / PACKAGE_NAME / PACKAGE_NAME / file.name
        if new_file.is_file():
            response = sg.popup_yes_no(f"WARNING\n\n{file.name} already exists in\n{new_file.parent}\n\n Overwrite?", **SG_KWARGS)
            if response == "No":
                continue
        if file.is_file():
            shutil.copy(file, new_file)
            print(f"✓ Copied {file.name} to {new_file.parent}")

def create_config_folder():
    """
    Uses click to find the most appropriate, platform independent folder
    for easyPyPI's config file.
    """
    # global CONFIG
    try:
        os.makedirs(CONFIG.parent)
        print(f"Folder created: {CONFIG.parent}")
    except FileExistsError:
        pass
    if not CONFIG.is_file():
        with open(CONFIG, "w") as file:
            json.dump({"AUTHOR": ""}, file)  # Create dummy .cfg file
        print(f"Created a new config file: {CONFIG}")

def update_config_file():
    """ Updates CONFIG (json) file based on repeatedly used global variables """
    create_config_folder()
    global CONFIG
    with open(CONFIG, "w") as file:
        global SCRIPT_PATH
        SCRIPT_PATH = str(SCRIPT_PATH)
        fields_dict = {x: globals().get(x) for x in CONFIG_FIELDS}
        SCRIPT_PATH = Path(SCRIPT_PATH)
        # json can't handle pathlib objects
        json.dump(fields_dict, file)
    print(f"✓ {CONFIG.name} updated")

def get_config_value(key):
    """ Returns a single value from the easyPyPI CONFIG file, or None """
    global CONFIG
    try:
        with open(CONFIG, "r") as file:
            config = json.load(file)
        return config.get(key)
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        # e.g. if file is empty or doesn't exist
        create_config_folder()
        return get_config_value(key)  # Try again!

def twine_setup():
    """
    Prompts for PyPI account setup and sets environment variables for Twine use.
    """
    if not get_config_value("TWINE_USERNAME"):
        urls = {"Test PyPI": r"https://test.pypi.org/account/register/",
                "PyPI": r"https://pypi.org/account/register/"}
        for repo, url in urls.items():
            response = sg.popup_yes_no(f"Do you need to register for an account on {repo}?",  **SG_KWARGS)
            if response == "Yes":
                print("Please register using the SAME USERNAME for PyPI as Test PyPI, then return to easyPyPI to continue the process.")
                webbrowser.open(url)
    response = sg.popup_get_text(f"Please enter your Twine username:", default_text = get_config_value("TWINE_USERNAME"), **SG_KWARGS)
    if not response:
        return
    global TWINE_USERNAME
    TWINE_USERNAME = response
    update_config_file()
    response = sg.popup_get_text("Please enter your Twine/PyPI password:", password_char = "*", default_text = get_config_value("TWINE_PASSWORD"), **SG_KWARGS)
    if not response:
        return
    global TWINE_PASSWORD
    TWINE_PASSWORD = response
    update_config_file()
    # ! BUG - not picking up existing TWINE_USERNAME

def create_distribution_package():
    """ Creates a .tar.gz distribution file with setup.py """
    try:
        import setuptools
        import twine
    except ImportError:
        print("> Installing setuptools and twine if not already present...")
        os.system('cmd /c "python -m pip install setuptools wheel twine"')
    os.chdir(SCRIPT_PATH / PACKAGE_NAME)
    print("> Running setup.py...")
    os.system('cmd /c "setup.py sdist"')

def upload_with_twine():
    """ Uploads to PyPI or Test PyPI with twine """
    choice = sg.popup(f"Do you want to upload {PACKAGE_NAME} to\nTest PyPI, or go FULLY PUBLIC on the real PyPI?\n", **SG_KWARGS, custom_text=("Test PyPI", "PyPI"))
    if choice == "PyPI":
        params = "pypi"
    if choice == "Test PyPI":
        params = "testpypi"
    if not choice:
        return
    params += f' dist/*-{VERSION}.tar.gz '
    if os.system(f'cmd /c "python -m twine upload --repository {params} -u {TWINE_USERNAME} -p {TWINE_PASSWORD}"'):
        # A return value of 1 (True) indicates an error
        print("Problem uploading with Twine; probably either:")
        print(" - An authentication issue.  Check your username and password?")
        print(" - Using an existing version number.  Try a new version number?")
    else:
        url = "https://"
        url += "" if choice == "PyPI" else "test."
        webbrowser.open(url + f"pypi.org/project/{PACKAGE_NAME}")
        response = sg.popup_yes_no("Fantastic! Your package should now be available in your webbrowser.\n\nDo you want to install it now using pip?\n", **SG_KWARGS)
        if response == "Yes":
            if not os.system(f'cmd /c "pip install -i https://test.pypi.org/simple/ {PACKAGE_NAME} --upgrade"'):
                # A return value of 1 indicates an error, 0 indicates success
                print(f"{PACKAGE_NAME} successfully installed using pip!\n")
                print(f"You can view its details using 'pip show {PACKAGE_NAME}'")
                os.system(f'cmd /c "pip show {PACKAGE_NAME}"')

def upload_to_github():
    """ Uploads package as a repository on Github """
    return
    # TODO

if __name__ == "__main__":
    # print = sg.Print
    sg.change_look_and_feel('DarkAmber')
    print(f"easyPyPI template files are locatedin:\n{HERE}")
    try:
        SCRIPT_PATH = get_config_value("SCRIPT_PATH") or Path().cwd()
    except json.decoder.JSONDecodeError:  # e.g. if file is empty
        SCRIPT_PATH = Path().cwd()
    with open(HERE / "setup_template.py", "r") as file:
        SCRIPT = file.readlines()
    create_new_script()
    update_config_file()
    create_folder_structure()
    create_essential_files()
    copy_existing_files()
    twine_setup()
    create_distribution_package()
    upload_with_twine()
    upload_to_github()

    # TODO:Refactor to avoid use of global variables e.g. Package/Session class?

    # TODO: Save "last session" package values to CONFIG?

    # TODO: Entry point for upversioning/updating package later on

    # TODO: Redirect os.system output to PySimpleGui Debug Window?

    # TODO: Implement config files instead of environment variables e.g.
    # https://github.com/json-transformations/jsonconfig

    # TODO: TWINE only supports 1 value pair, not one for Test and one for PyPI
    # Maybe refactor to use .pypirc config files?
    # https://packaging.python.org/specifications/pypirc/#common-configurations

    # TODO: Import defaults from README_template, test_template, init_template
    # to enable easier editing/personalisation, rather than hard coding their
    # template values as strings in create_essential_file().

    # TODO: Offer other schemas in get_next_version_number e.g. date format:
    # 2020.21.11

    # TODO: Save password securely
