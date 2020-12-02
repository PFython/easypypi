import datetime
import json
import os
import shutil
import webbrowser
from decimal import Decimal as decimal
from pathlib import Path
import click  # used to get cross-platform folder path for config file
import PySimpleGUI as sg

from cleverdict import CleverDict
from shared_functions import create_file, update_line
from classifiers import classifier_list
from licenses import licenses_dict
from setup_template import (AUTHOR, CLASSIFIERS, DESCRIPTION, EMAIL, GITHUB_ID,
                            KEYWORDS, LICENSE, PACKAGE_NAME, REQUIREMENTS, URL,
                            VERSION, HERE)

class Session(CleverDict):
    """
    Stores information about the current project as well as persistent
    variables such as email address that are unlikely to change often
    for a typical user.

    Makes use of CleverDict's auto-save feature to store values in a config
    file, and .get_aliases() to keep a track of newly created attributes.
    """
    config_path = Path(click.get_app_dir("easyPyPI")) / ("config.json")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.create_config_file()
        self.load_value("script_path_str")
        if not self.script_path_str:  # Placeholder for final setup.py path
            self.script_path_str = os.getcwd()
        self.here_path_str = str(Path(__file__).parent)
        with open(self.here_path / "setup_template.py", "r") as file:
            self.script = file.readlines()

    def __str__(self):
        output = self.info(as_str=True)
        return output.replace("CleverDict", type(self).__name__, 1)

    def save(self, key: str, value: any):
        """
        This method is called by CleverDict whenever a value or attribute
        changes.  Used here to update the config file automatically.
        """
        with open(Session.config_path, "w") as file:
            # CleverDict.get_aliases finds attributes created after __init__:
            fields_dict = {x: self.get(x) for x in self.get_aliases() if "PASSWORD" not in x}
            json.dump(fields_dict, file)
        print(f"✓ '{key}' updated in {Session.config_path}")
        # TODO: Save password securely e.g. with keyring

    def create_config_file(self):
        """
        Uses click to find & create a platform-appropriate easyPyPI folder, then
        creates a skeleton json file there to store persistent data (if one
        doesn't already exist, or if the current one is empty).
        """
        try:
            os.makedirs(Session.config_path.parent)
            print(f"Folder created: {Session.config_path.parent}")
        except FileExistsError:
            pass
        if Session.config_path.is_file() and Session.config_path.stat().st_size:
            # config file exists and isn't empty
            return
        with open(Session.config_path, "w") as file:
            json.dump({"author": ""}, file)  # Create skeleton .json file
        print(f"Created a new config file: {Session.config_path}")

    def load_value(self, key):
        """
        Loads a value from the config file and updates the relevant attribute.
        """
        try:
            with open(Session.config_path, "r") as file:
                value = json.load(file).get(key)
                if value:
                    setattr(self, key, value)
                else:
                    print(f"\n⚠   Failed to find '{key}' in:\n    {Session.config_path}")
        except (json.decoder.JSONDecodeError, FileNotFoundError):
            # e.g. if file is empty or doesn't exist
            return

    @property
    def script_path(self):
        """
        json.dump can't serialise pathlib objects so this method creates them
        from script_path_str.

        This approach ensures the property doesn't appear in .get_aliases which
        is used for deciding what attributes get auto-saved to the config file.
        """
        return Path(self.script_path_str)

    @property
    def here_path(self):
        """
        json.dump can't serialise pathlib objects so this method creates them
        from here_path_str.

        This approach ensures the property doesn't appear in .get_aliases which
        is used for deciding what attributes get auto-saved to the config file.
        """
        return Path(self.here_path_str)

    def delete_config_file(self):
        """
        Deletes the easyPyPI config file e.g. in case of corruption.
        Creating a new Session object will automatically recreate a fresh one.
        """
        os.remove(Session.config_path)

    def get_default_package_name(self):
        return "as_easy_as_pie"

    def get_default_version(self):
        return get_next_version_number(VERSION)

    def get_default_github_id(self):
        return

    def get_default_url(self):
        default = f"https://github.com/{self.load_value('github_id')}"
        return default + f"/{self.load_value('package_name')}"

    def get_default_description(self):
        return

    def get_default_author(self):
        return

    def get_default_email(self):
        return

    def get_default_keywords(self):
        default = f"{self.load_value('package_name')}, "
        default += f"{self.load_value('author')}, "
        return default + f"{self.load_value('github_id')}, "

    def get_default_requirements(self):
        return "cleverdict, "

    def get_metadata(self):
        """
        Check config file for previous values.  If no value is set, prompts for
        a value and updates the relevant Session attribute.
        """
        prompts = {"PACKAGE_NAME": "Please enter a name for this package:",
                   "VERSION": "Please enter latest version number:",
                   "GITHUB_ID": "Please enter your Github ID:",
                   "URL": "Please enter a link to the package repository:",
                   "DESCRIPTION": "Please enter a description:",
                   "AUTHOR": "Please the full name of the author:",
                   "EMAIL": "Please enter an email address for the author:",
                   "KEYWORDS": "Please enter some keywords separated by a comma:",
                   "REQUIREMENTS": "Please enter any packages/modules that absolutely need to be installed for yours to work, separated by commas:"}
        for key, prompt in prompts.items():
            default = self.load_value(key)
            if not default:
                func = getattr(self, "get_default_" + key.lower())
                default = func()
            old_line_starts = key.upper() + " = "
            new = sg.popup_get_text(prompt, default_text = default, **sg_kwargs)
            self.script = update_line(self.script, old_line_starts, new)

    def get_classifiers(self):
        """
        Selects classifiers in key categories to better describe the package.
        Choices are imported from classifiers.classifier_list.
        Updates made in place to .classifiers list
        """
        self.load_value("classifiers")
        if not self.classifiers:
            self.classifiers = []
        else:  # str -> list
            self.classifiers = eval(self.classifiers)
        for group in "Development Status|Intended Audience|Operating System|Programming Language :: Python|Topic".split("|"):
            choices = [x for x in classifier_list if x.startswith(group)]
            self.classifiers.extend(prompt_with_checkboxes(group, choices))
        self.classifiers = ", ".join(self.classifiers)

    def get_license(self):
        """
        Select from a shortlist of common license types
        Choices are imported from license.licenses_dict.
        Updates made in place to .license
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
            if LICENSE:
                LICENSE = finalise_license(LICENSE)
            SCRIPT = update_line(SCRIPT, "LICENSE = ", LICENSE.name)

### STATIC METHODS

def get_next_version_number(current_version):
    """ Suggests next package version number based on simple schemas """
    decimal_version = decimal(str(current_version))
    try:
        _, digits, exponent =decimal_version.as_tuple()
        if exponent == 0:  # i.e. 0 decimal places:
            increment = "0.1"
        else:
            increment = "0.01"
        return str(decimal_version + decimal(increment))
    except dec.InvalidOperation:
        return new_version+"-new"

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


    # TODO: Select checkboxes based on config file

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
                        "[fullname]": author}
    if license.key in ['gpl-3.0', 'lgpl-3.0', 'agpl-3.0']:
        replacements = {"<year>": year,
                        "<name of author>": author,
                        "<program>": package_name,
                        "Also add information on how to contact you by electronic and paper mail.": f"    Contact email: {EMAIL}",
                        "<one line to give the program's name and a brief idea of what it does.>": f"{package_name}: {DESCRIPTION}"}
    if license.key == "apache-2.0":
        replacements = {"[yyyy]": year,
                        "[name of copyright owner]": author}
    if replacements:
        for old, new in replacements.items():
            license.body = license.body.replace(old, new)
    return license

def create_folder_structure():
    """
    Creates skeleton folder structure for a package and starter files.
    Updates global variable SCRIPT_PATH.
    """
    script_path  = Path(sg.popup_get_folder("Please select the parent folder for your package i.e. without the package name", default_path = script_path, **sg_kwargs))
    update_config_file()
    new_folder = script_path / package_name / package_name
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
    /package_name/__init__.py
    /package_name/package_name.py
    /package_name/test_PACKAGE_NAME.py
    """
    package_path = script_path / package_name
    create_file(package_path / package_name / "__init__.py", [f"from {package_name} import *"])
    create_file(package_path / package_name / (package_name + ".py"), [f"# {package_name} by {author}\n", f"# {datetime.datetime.now()}\n"])
    create_file(package_path / package_name / ("test_" +package_name + ".py"), [f"# Tests for {package_name}\n", "\n", f"from {package_name} import *\n", "import pytest\n", "", "class Test_Group_1:\n", "    def test_something(self):\n", '        """ Something should happen when you run something() """\n', "        assert something() == something_else\n"])
    create_file (package_path / "README.md", [f"# {package_name}\n", DESCRIPTION+"\n\n", "### OVERVIEW\n\n", "### INSTALLATION\n\n", "### BASIC USE\n\n", "### UNDER THE BONNET\n\n", "### CONTRIBUTING\n\n", f"Contact {author} {EMAIL}\n\n", "### CREDITS\n\n"])
    # setup.py and LICENSE should always be overwritten as most likely to
    # include changes from running easyPiPY.
    # The other files are just bare-bones initially, created as placeholders.
    create_file(package_path / "setup.py", SCRIPT, overwrite = True)
    create_file(package_path / "LICENSE", LICENSE.body, overwrite=True)

def copy_existing_files():
    """
    Prompts for additional files to copy over into the newly created folder:
    \package_name\package_name
    """
    files = sg.popup_get_file("Please select any other files to copy to new project folder", **sg_kwargs, default_path="", multiple_files=True)
    for file in [Path(x) for x in files.split(";")]:
        new_file = script_path / package_name / package_name / file.name
        if new_file.is_file():
            response = sg.popup_yes_no(f"WARNING\n\n{file.name} already exists in\n{new_file.parent}\n\n Overwrite?", **sg_kwargs)
            if response == "No":
                continue
        if file.is_file():
            shutil.copy(file, new_file)
            print(f"✓ Copied {file.name} to {new_file.parent}")

def twine_setup():
    """
    Prompts for PyPI account setup and sets environment variables for Twine use.
    """
    if not load_value("TWINE_USERNAME"):
        urls = {"Test PyPI": r"https://test.pypi.org/account/register/",
                "PyPI": r"https://pypi.org/account/register/"}
        for repo, url in urls.items():
            response = sg.popup_yes_no(f"Do you need to register for an account on {repo}?",  **sg_kwargs)
            if response == "Yes":
                print("Please register using the SAME USERNAME for PyPI as Test PyPI, then return to easyPyPI to continue the process.")
                webbrowser.open(url)
    response = sg.popup_get_text(f"Please enter your Twine username:", default_text = load_value("TWINE_USERNAME"), **sg_kwargs)
    if not response:
        return
    global TWINE_USERNAME
    TWINE_USERNAME = response
    update_config_file()
    response = sg.popup_get_text("Please enter your Twine/PyPI password:", password_char = "*", default_text = load_value("TWINE_PASSWORD"), **sg_kwargs)
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
    os.chdir(script_path / package_name)
    print("> Running setup.py...")
    os.system('cmd /c "setup.py sdist"')

def upload_with_twine():
    """ Uploads to PyPI or Test PyPI with twine """
    choice = sg.popup(f"Do you want to upload {package_name} to\nTest PyPI, or go FULLY PUBLIC on the real PyPI?\n", **sg_kwargs, custom_text=("Test PyPI", "PyPI"))
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
        webbrowser.open(url + f"pypi.org/project/{package_name}")
        response = sg.popup_yes_no("Fantastic! Your package should now be available in your webbrowser.\n\nDo you want to install it now using pip?\n", **sg_kwargs)
        if response == "Yes":
            if not os.system(f'cmd /c "pip install -i https://test.pypi.org/simple/ {package_name} --upgrade"'):
                # A return value of 1 indicates an error, 0 indicates success
                print(f"{package_name} successfully installed using pip!\n")
                print(f"You can view its details using 'pip show {package_name}'")
                os.system(f'cmd /c "pip show {package_name}"')
    # TODO: Automate registration with https://mechanicalsoup.readthedocs.io/

def upload_to_github():
    """ Uploads package as a repository on Github """
    return
    # TODO
    # https://mechanicalsoup.readthedocs.io/

def start_gui(redirect=False):
    """
    Toggles between normal output and routing stdout/stderr to PySimpleGUI
    """
    if redirect:
        global print
        print = sg.Print
    # Common keyword arguments for PySimpleGUI popups:
    global sg_kwargs
    sg_kwargs = {"title": "easyPyPI", "keep_on_top": True, "icon": HERE / "easypypi.ico"}
    sg.change_look_and_feel('DarkAmber')
    # Redirect stdout and stderr to Debug Window:
    sg.set_options(message_box_line_width=80, debug_win_size=(100,30),)
    options = {"do_not_reroute_stdout": False, "keep_on_top": True}
    print(f"easyPyPI template files are located in:\n{Path(__file__).parent}", **options if redirect else {})

start_gui(redirect=False)

if __name__ == "__main__":
    self = Session()
    self.get_metadata()
    update_config_file()
    create_folder_structure()
    create_essential_files()
    copy_existing_files()
    twine_setup()
    create_distribution_package()
    upload_with_twine()
    upload_to_github()


    # TODO: Entry point for upversioning/updating package later on

    # TODO: Redirect os.system output to PySimpleGui Debug Window?

    # TODO: TWINE only supports 1 value pair, not one for Test and one for PyPI
    # Maybe refactor to use .pypirc config files?
    # https://packaging.python.org/specifications/pypirc/#common-configurations

    # TODO: Import defaults from README_template, test_template, init_template
    # to enable easier editing/personalisation, rather than hard coding their
    # template values as strings in create_essential_file().

    # TODO: Offer other schemas in get_next_version_number e.g. date format:
    # 2020.21.11



