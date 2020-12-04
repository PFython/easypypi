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

class Package(CleverDict):
    """
    Methods and data relating to a Python module/package in preparation for
    publishing on the Python Package Index (PyPI).

    Makes use of CleverDict's auto-save feature to store values in a config
    file, and .get_aliases() to keep a track of newly created attributes.
    """
    config_path = Path(click.get_app_dir("easyPyPI")) / ("config.json")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__class__.create_config_file()
        if not self.load_value("script_path_str"):
            # Placeholder for final setup.py path:
            self.script_path_str = os.getcwd()
        self.here_path_str = str(Path(__file__).parent)
        with open(self.here_path / "setup_template.py", "r") as file:
            self.script = file.readlines()

    def __str__(self):
        output = self.info(as_str=True)
        return output.replace("CleverDict", type(self).__name__, 1)

    @classmethod
    def load_config_file(cls):
        """
        Loads the contents of a pre-existing config file as attributes

        Class method allows access to config file even if there are problems instantiating a Package object.
        """
        with open(cls.config_path, "r") as file:
                values = json.load(file)
        for key, value in values.items():
            setattr(self, key, value)

    @classmethod
    def create_config_file(cls):
        """
        Uses click to find & create a platform-appropriate easyPyPI folder, then
        creates a skeleton json file there to store persistent data (if one
        doesn't already exist, or if the current one is empty).

        Class method allows access to config file even if there are problems instantiating a Package object.
        """
        if cls.config_path.is_file() and cls.config_path.stat().st_size:
            # config file exists and isn't empty
            cls.__class__.load_config_file()
            return
        try:
            os.makedirs(cls.config_path.parent)
            print(f"Folder created: {cls.config_path.parent}")
        except FileExistsError:
            pass
        with open(cls.config_path, "w") as file:
            json.dump({"author": ""}, file)  # Create skeleton .json file
        print(f"Created a new config file: {cls.config_path}")

    @classmethod
    def delete_config_file(cls):
        """
        Deletes the easyPyPI config file e.g. in case of corruption.
        Creating a new Package object will automatically recreate a fresh one.

        Class method allows access to config file even if there are problems instantiating a Package object.
        """
        os.remove(cls.config_path)

    def save(self, key: str, value: any):
        """
        This method is called by CleverDict whenever a value or attribute
        changes.  Used here to update the config file automatically.
        """
        with open(Package.config_path, "w") as file:
            # CleverDict.get_aliases finds attributes created after __init__:
            fields_dict = {x: self.get(x) for x in self.get_aliases() if "PASSWORD" not in x}
            json.dump(fields_dict, file)
        print(f"✓ '{key}' updated in {Package.config_path}")
        # TODO: Save password securely e.g. with keyring

    def load_value(self, key):
        """
        Loads a value from the config file and updates the relevant attribute.
        Also returns the value, or None.
        """
        try:
            with open(Package.config_path, "r") as file:
                value = json.load(file).get(key)
                if value:
                    setattr(self, key, value)
                    return value
                else:
                    print(f"\n⚠   Failed to find '{key}' in:\n    {Package.config_path}")
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

    def get_default_name(self):
        return "as_easy_as_pie"

    def get_default_version(self):
        return get_next_version_number(VERSION)

    def get_default_github_id(self):
        return

    def get_default_url(self):
        default = f"https://github.com/{self.github_id}"
        return default + f"/{self.name}"

    def get_default_description(self):
        return

    def get_default_author(self):
        return

    def get_default_email(self):
        return

    def get_default_keywords(self):
        default = f"{self.name}, "
        default += f"{self.author}, "
        return default + f"{self.github_id}, "

    def get_default_requirements(self):
        return "cleverdict, "

    def bypass_metadata_review(self):
        """
        Check if all metadata has been supplied previously, and if so gives the
        option to bypass get_metadata() and move straight to upversioning.

        Returns True to bypass metadata review, False to proceed as normal.
        """
        fields = "name version github_id url description author email keywords requirements license classifiers twine_username".split()
        fields_exist = [hasattr(self, x) for x in fields]
        if all(fields_exist) and self.script_path.exists():
            #  Check this path test is valid!
            response = sg.popup_yes_no(f"Full metadata already exists for package '{self.name}'.\n\nSkip metadata review steps?", **sg_kwargs)
            if response is None:
                quit()
            return True if response == "Yes" else False

    def get_metadata(self):
        """
        Check config file for previous values.  If no value is set, prompts for
        a value and updates the relevant Package attribute.
        """
        prompts = {"name": "Please enter a name for this package (all lowercase, underscores if needed):",
                   "version": "Please enter latest version number:",
                   "github_id": "Please enter your Github or main repository ID:",
                   "url": "Please enter a link to the package repository:",
                   "description": "Please enter a description:",
                   "author": "Please the full name of the author:",
                   "email": "Please enter an email address for the author:",
                   "keywords": "Please enter some keywords separated by a comma:",
                   "requirements": "Please enter any packages/modules that absolutely need to be installed for yours to work, separated by commas:"}
        for key, prompt in prompts.items():
            default = self.load_value(key)
            if not default:
                func = getattr(self, "get_default_" + key.lower())
                default = func()
            old_line_starts = key.upper() + " = "
            new = sg.popup_get_text(prompt, default_text = default, **sg_kwargs)
            if new is None:
                quit()
            setattr(self, key, new)
            self.script = update_line(self.script, old_line_starts, new)

    def get_classifiers(self):
        """
        Selects classifiers in key categories to better describe the package.
        Choices are imported from classifiers.classifier_list.

        Updates made in place to .classifiers comma-separated string
        """
        self.load_value("classifiers")
        if not hasattr(self, "classifiers"):
            classifiers = ""
        else:
            classifiers =  [x.strip() for x in self.classifiers.split(",")]
        for group in "Development Status|Intended Audience|Operating System|Programming Language :: Python|Topic".split("|"):
            choices = [x for x in classifier_list if x.startswith(group)]
            selection = prompt_with_checkboxes(group, choices)
            classifiers.update(selection)
        self.classifiers = ", ".join(classifiers)
        # TODO: Pre-select checkboxes based on last saved config file

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
        layout += [[sg.Button("OK")]]
        window = sg.Window("easypypi", layout, size = (600,400),resizable=True)
        while True:
            event, values  =  window.read(close=True)
            if event == "OK" and any(values.values()):
                window.close()
                self.license = [licenses[k] for k,v in values.items() if v][0]
                break
            if event:
                if "http" in event:
                    webbrowser.open(event)
            else:
                window.close()
                self.license = licenses[0]  # Default license
                print(f"\nDefault license selected: {self.license.name}")
                break
        self.finalise_license()
        self.script = update_line(self.script, "LICENSE = ", self.license.name)
        # TODO: Pre-select radio button based on last saved config file

    def finalise_license(self):
        """ Make simple updates based on license.implementation instructions """
        year = str(datetime.datetime.now().year)
        replacements = dict()
        if self.license.key == 'lgpl-3.0':
            self.license.body += '\nThis license is an additional set of permissions to the <a href="/licenses/gpl-3.0">GNU GPLv3</a> license which is reproduced below:\n\n'
            gpl = [CleverDict(x) for x in licenses_dict if x['key'] == 'gpl-3.0'][0]
            self.license.body += gpl.body
        if self.license.key == "mit":
            replacements = {"[year]": year,
                            "[fullname]": self.author}
        if self.license.key in ['gpl-3.0', 'lgpl-3.0', 'agpl-3.0']:
            replacements = {"<year>": year,
                            "<name of author>": self.author,
                            "<program>": self.name,
                            "Also add information on how to contact you by electronic and paper mail.": f"    Contact email: {self.email}",
                            "<one line to give the program's name and a brief idea of what it does.>": f"{self.name}: {self.description}"}
        if self.license.key == "apache-2.0":
            replacements = {"[yyyy]": year,
                            "[name of copyright owner]": self.author}
        if replacements:
            for old, new in replacements.items():
                self.license.body = self.license.body.replace(old, new)
        return license

    def create_folder_structure(self):
        """
        Creates skeleton folder structure for a package and starter files.
        Updates global variable SCRIPT_PATH.
        """
        # Check if script_path is correct...
        script_path  = Path(sg.popup_get_folder("Please select the parent folder for your package i.e. without the package name", default_path = self.script_path, **sg_kwargs))
        new_folder = script_path / self.name / self.name
        try:
            os.makedirs(new_folder)
            print(f"Created package folder {new_folder}")
        except FileExistsError:
            print(f"Folder already exists {new_folder}")

    def copy_other_files():
        """
        Prompts for additional files to copy over into the newly created folder:
        \package_name\package_name
        """
        files = sg.popup_get_file("Please select any other files to copy to new project folder", **sg_kwargs, default_path="", multiple_files=True)
        for file in [Path(x) for x in files.split(";")]:
            new_file = self.script_path / self.name / self.name / file.name
            if new_file.is_file():
                response = sg.popup_yes_no(f"WARNING\n\n{file.name} already exists in\n{new_file.parent}\n\n Overwrite?", **sg_kwargs)
                if response == "No":
                    continue
            if file.is_file():
                shutil.copy(file, new_file)
                print(f"✓ Copied {file.name} to {new_file.parent}")

    def create_essential_files(self):
        """
        Creates essential files for the new package:
        /setup.py
        /README.md
        /LICENSE
        /package_name/__init__.py
        /package_name/package_name.py
        /package_name/test_PACKAGE_NAME.py
        """
        self.package_path = self.script_path_str / self.name
        create_file(self.package_path / self.name / "__init__.py", [f"from {self.name} import *"])
        create_file(self.package_path / self.name / (self.name + ".py"), [f"# {self.name} by {self.author}\n", f"# {datetime.datetime.now()}\n"])
        create_file(self.package_path / self.name / ("test_" +self.name + ".py"), [f"# Tests for {self.name}\n", "\n", f"from {self.name} import *\n", "import pytest\n", "", "class Test_Group_1:\n", "    def test_something(self):\n", '        """ Something should happen when you run something() """\n', "        assert something() == something_else\n"])
        create_file (self.package_path / "README.md", [f"# {self.name}\n", DESCRIPTION+"\n\n{self.description}", "### OVERVIEW\n\n", "### INSTALLATION\n\n", "### BASIC USE\n\n", "### UNDER THE BONNET\n\n", "### CONTRIBUTING\n\n", f"Contact {self.author} {self.email}\n\n", "### CREDITS\n\n"])
        # setup.py and LICENSE should always be overwritten as most likely to
        # include changes from running easyPiPY.
        # The other files are just bare-bones initially, created as placeholders.
        create_file(self.package_path / "setup.py", self.script, overwrite = True)
        create_file(self.package_path / "LICENSE", self.license.body, overwrite=True)

    def twine_setup(self):
        """
        Prompts for PyPI account setup and sets environment variables for Twine use.
        """
        if not load_value("twine_username"):
            urls = {"Test PyPI": r"https://test.pypi.org/account/register/",
                    "PyPI": r"https://pypi.org/account/register/"}
            for repo, url in urls.items():
                response = sg.popup_yes_no(f"Do you need to register for an account on {repo}?",  **sg_kwargs)
                if response == "Yes":
                    print("Please register using the SAME USERNAME for PyPI as Test PyPI, then return to easyPyPI to continue the process.")
                    webbrowser.open(url)
        response = sg.popup_get_text(f"Please enter your Twine username:", default_text = load_value("twine_username"), **sg_kwargs)
        if not response:
            return
        self.twine_username = response
        response = sg.popup_get_text("Please enter your Twine/PyPI password:", password_char = "*", default_text = load_value("twine_password"), **sg_kwargs)
        if not response:
            return
        self.twine_password = response
        # ! BUG - not picking up existing twine_username

    def create_distribution_package(self):
        """ Creates a .tar.gz distribution file with setup.py """
        try:
            import setuptools
            import twine
        except ImportError:
            print("> Installing setuptools and twine if not already present...")
            os.system('cmd /c "python -m pip install setuptools wheel twine"')
        os.chdir(self.script_path / self.name)
        print("> Running setup.py...")
        os.system('cmd /c "setup.py sdist"')

    def upload_with_twine(self):
        """ Uploads to PyPI or Test PyPI with twine """
        choice = sg.popup(f"Do you want to upload {self.name} to\nTest PyPI, or go FULLY PUBLIC on the real PyPI?\n", **sg_kwargs, custom_text=("Test PyPI", "PyPI"))
        if choice == "PyPI":
            params = "pypi"
        if choice == "Test PyPI":
            params = "testpypi"
        if not choice:
            return
        params += f' dist/*-{self.version}.tar.gz '
        if os.system(f'cmd /c "python -m twine upload --repository {params} -u {self.twine_username} -p {self.twine_password}"'):
            # A return value of 1 (True) indicates an error
            print("Problem uploading with Twine; probably either:")
            print(" - An authentication issue.  Check your username and password?")
            print(" - Using an existing version number.  Try a new version number?")
        else:
            url = "https://"
            url += "" if choice == "PyPI" else "test."
            webbrowser.open(url + f"pypi.org/project/{self.name}")
            response = sg.popup_yes_no("Fantastic! Your package should now be available in your webbrowser.\n\nDo you want to install it now using pip?\n", **sg_kwargs)
            if response == "Yes":
                if not os.system(f'cmd /c "pip install -i https://test.pypi.org/simple/ {self.name} --upgrade"'):
                    # A return value of 1 indicates an error, 0 indicates success
                    print(f"{self.name} successfully installed using pip!\n")
                    print(f"You can view its details using 'pip show {self.name}'")
                    os.system(f'cmd /c "pip show {self.name}"')
        # TODO: Automate registration: https://mechanicalsoup.readthedocs.io/

    def upload_to_github(self):
        """ Uploads package as a repository on Github """
        return
        # TODO: Automate registration: https://mechanicalsoup.readthedocs.io/

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
    Returns a set of selected choices, or and empty set
    """
    prompt = [sg.Text(text=f"Please select any relevant classifiers in the {group.title()} group:")]
    layout = [[sg.Checkbox(text=choice)] for choice in choices]
    buttons = [sg.Button("Next")]
    event, checked  =  sg.Window("easypypi", [prompt,[sg.Column(layout, scrollable=True, vertical_scroll_only=True, size= (600,300))], buttons], size= (600,400),resizable=True).read(close=True)
    if event == "Next":
        return {choices[k] for k,v in checked.items() if v}
    else:
        return set()
    # TODO: Pre-select checkboxes based on last saved config file

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

if __name__ == "__main__":
    # start_gui(redirect=True)
    start_gui()
    self = Package()
    if not self.bypass_metadata_review():
        self.get_metadata()
        self.get_classifiers()
        self.get_license()
        self.create_folder_structure()
        self.copy_other_files()
    else:
        self.version = get_next_version_number(self.version)
    self.create_essential_files()
    self.twine_setup()
    self.create_distribution_package()
    self.upload_with_twine()
    self.upload_to_github()

### FUTURE ENHANCEMENTS

# TODO: TWINE only supports 1 value pair, not one for Test and one for PyPI
# Maybe refactor to use .pypirc config files?
# https://packaging.python.org/specifications/pypirc/#common-configurations

# TODO: Import defaults from README_template, test_template, init_template
# to enable easier editing/personalisation, rather than hard coding their
# template values as strings in create_essential_file().

# TODO: Offer other schemas in get_next_version_number e.g. date format:
# 2020.21.11



