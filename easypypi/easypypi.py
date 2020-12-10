import datetime
import getpass
import json
import os
import shutil
import webbrowser
from decimal import Decimal as decimal
from pathlib import Path

import PySimpleGUI as sg
import click  # used to get cross-platform folder path for config file
import mechanicalsoup
from cleverdict import CleverDict

from .licenses import filename
from .utils import EASYPYPI_FIELDS
from .utils import GROUP_CLASSIFIERS
from .utils import REPLACEMENTS
from .utils import SETUP_FIELDS
from .classifiers import classifier_list
from .shared_functions import create_file
from .shared_functions import update_line

# Global keyword arguments for PySimpleGUI popups:
sg_kwargs = {
    "title": "easyPyPI",
    "keep_on_top": True,
    "icon": Path(__file__).parent.parent / "easypypi.ico",
}


class Package(CleverDict):
    """
    Methods and data relating to a Python module/package in preparation for
    publishing on the Python Package Index (PyPI).

    Makes use of CleverDict's auto-save feature to store values in a config
    file, and .get_aliases() to keep a track of newly created attributes.

    Exits early if prompts == False

    redirect : Send stdout and stderr to PySimpleGUI Debug Window

    """

    easypypi_dirpath = Path(__file__).parent
    config_filepath = Path(click.get_app_dir("easyPyPI")) / ("config.json")
    setup_fields = SETUP_FIELDS

    def __init__(self, name=None, **kwargs):
        if "prompts" in kwargs:
            prompts = kwargs['prompts']
            del kwargs["prompts"]
        else:
            prompts = True
        super().__init__(**kwargs)
        # Caution! If kwargs are supplied, autosave will overwrite JSON confi
        self.start_gui(redirect=kwargs.get("redirect"))
        self.load_defaults(name, prompts)
        # As above... must Load before Setting any other values with autosave on
        if self.name and self.get("setup_filepath_str"):
            if prompts is not False:
                self.review()
                self.generate()
                self.upload()
        self.summary()
        # Force reset of 'prompts' option in JSON config:
        self.prompts = True

    def summary(self):
        """ Prints a summary of key fields which have not yet been set """
        fields = EASYPYPI_FIELDS + SETUP_FIELDS
        msg = ["."+ x for x in fields if not self.get(x)]
        if not msg:
            msg = "\n✓ All essential values have been set.\n  "
        else:
            msg = ["\n⚠ The following values have not yet been set:\n  "] + msg
            msg = "\n  ".join(msg) + "\n"
        print(msg)

    def start_gui(self, **kwargs):
        """
        Toggles between normal output and routing stdout/stderr to PySimpleGUI
        """
        if kwargs.get("redirect"):
            global print
            print = sg.Print
        sg.change_look_and_feel("DarkAmber")
        # Redirect stdout and stderr to Debug Window:
        sg.set_options(
            message_box_line_width=80,
            debug_win_size=(100, 30),
        )
        options = {"do_not_reroute_stdout": False, "keep_on_top": True}
        print(
            f"\nⓘ easyPyPI template files are located in:\n  {self.__class__.easypypi_dirpath}",
            **options if kwargs.get("redirect") else {},
        )
        print(f"\nⓘ Your easyPyPI config file is:\n  {self.__class__.config_filepath}")

    def load_defaults(self, name=None, prompts = True):
        """
        Entry point for loading default Package values as attributes.
        Choose between last updated JSON config file, and setup.py if it exists.

        Exits early if prompts == False
        """
        self.create_skeleton_config_file()
        # Important!  Defaults must be loaded from file (if possible) first:
        self.load_defaults_from_config_file()
        if name:
            self.name = name
        if not self.get("name"):
            self.name = sg.popup_get_text(
                "Please enter a name for this package (all lowercase, underscores if needed):",
                default_text="as_easy_as_pie",
                **sg_kwargs,
            )
        if prompts and self.name:
            self.create_folder_structure()
            if self.setup_filepath.is_file() and self.setup_filepath.stat().st_size:
                # setup.py exists & isn't empty, overwrite default values
                self.load_defaults_from_setup_py()

    def create_skeleton_config_file(self):
        """
        Uses click to find & create a platform-appropriate easyPyPI folder, then
        creates a skeleton json file there to store persistent data (if one
        doesn't already exist or if the current one is empty).
        """
        if (
                self.__class__.config_filepath.is_file()
                and self.__class__.config_filepath.stat().st_size
        ):
            return
        try:
            os.makedirs(self.__class__.config_filepath.parent)
            print(f"ⓘ Folder created:\n {self.__class__.config_filepath.parent}")
        except FileExistsError:
            pass
        with open(self.__class__.config_filepath, "w") as file:
            json.dump({"version": "0.1"}, file)  # Create skeleton .json file
        print(f"\n⚠ Skeleton config file created:\n  {self.__class__.config_filepath}")

    def load_defaults_from_config_file(self):
        """
        Loads default metadata from last updated config file.
        Creates .scriptlines as a copy of setup_template.py
        """
        with open(self.__class__.config_filepath, "r") as file:
            values = json.load(file)
        for key, value in values.items():
            setattr(self, key, value)
        setup = self.__class__.easypypi_dirpath / "setup_template.py"
        with open(setup, "r") as file:
            self.script_lines = file.readlines()

    def create_folder_structure(self):
        """
        Creates skeleton folder structure for a package and starter files.
        Creates .setup_filepath_str.
        """
        if not hasattr(self, "setup_filepath"):
            self.setup_filepath_str = str(Path.cwd() / self.name / "setup.py")
        parent_path_str = ""
        while not parent_path_str:
            parent_path_str = sg.popup_get_folder(
                "Please select the parent folder for your package i.e. WITHOUT the package name",
                default_path=self.get_default_filepath(),
                **sg_kwargs,
            )
            if parent_path_str is None:
                return
        setup_dirpath = Path(parent_path_str) / self.name
        self.setup_filepath_str = str(setup_dirpath / "setup.py")
        try:
            os.makedirs(setup_dirpath / self.name)
            print(f"\n✓ Created package folder:\n  {setup_dirpath}")
        except FileExistsError:
            print(f"\nⓘ Package folder already exists:\n  {setup_dirpath}")

    def load_defaults_from_setup_py(self):
        """
        Loads default metadata from previously created setup.py
        Creates .scriptlines as a copy of setup.py
        """
        with open(self.setup_filepath, "r") as file:
            lines = file.readlines()
        for line in lines:
            for field in self.__class__.setup_fields:
                if line.startswith(field.upper() + " = "):
                    # Use eval in case the value isn't simply a string:
                    setattr(self, field, eval(line.split(" = ")[-1]))
        with open(self.setup_filepath, "r") as file:
            self.script_lines = file.readlines()

    def review(self):
        """
        Entry point for creating a package for the first time, or reviewing
        basic metadata for a previously created package.
        """
        self.check_account_credentials("github_")  # sets self.github_username
        self.get_metadata()
        self.get_license()
        self.get_classifiers()
        self.upversioned_already = True

    def generate(self):
        """
        Entry point for upversioning an existing package, recreating
        setup.py and creating a new tar.gz package ready for uploading.
        """
        self.copy_other_files()
        choice = sg.popup_yes_no(
            "Do you want to generate new package files "
            "(setup.py, README, LICENSE, tar.gz, etc) from the current metadata?\n",
            **sg_kwargs,
        )
        if choice != "Yes":
            return
        if not self.get("upversioned_already"):
            self.version = self.next_version
        self.upversioned_already = False  # reset for next time
        self.create_essential_files()
        self.run_setup_py()

    def upload(self):
        """
        Entry point for republishing an existing package to Test PyPI or PyPI.
        """
        self.upload_with_twine()
        self.create_github_repository()
        self.upload_to_github()

    def save(self, key=None, value=None):
        """
        This method is called by CleverDict whenever a value or attribute
        changes.  Used here to update the config file automatically.

        NB because values are loaded from the config file into attributes during
        __init__, if you want to DELETE an entry from the config file e.g.
        during debugging you'll need to delete the attribute then run .save:

        del self.x
        self.save()
        """
        with open(self.__class__.config_filepath, "w") as file:
            # CleverDict.get_aliases finds attributes created after __init__:
            fields_dict = {
                x: self.get(x)
                for x in self.get_aliases()
                if "password" not in x.lower()
            }
            json.dump(fields_dict, file)
        if key:
            if "password" in key.lower():
                location = "memory but NOT saved to file"
            else:
                location = self.__class__.config_filepath
            # Enable to confirm auto-save is working:
            # print(f"ⓘ '{key}' updated in {location}")

    @property
    def setup_filepath(self):
        """
        json.dump can't serialise pathlib objects so this method creates them
        from setup_filepath_str.

        This approach ensures the property doesn't appear in .get_aliases which
        is used for deciding what attributes get auto-saved to the config file.
        """
        return Path(self.setup_filepath_str)

    def get_default_filepath(self):
        path = Path(self.get("setup_filepath_str") or Path().cwd())
        # Default path should be the parent of self.name and not include it
        while path.parts[-1] in [self.name, "setup.py"]:
            path = Path().joinpath(*path.parts[:-1])
        return str(path)

    def get_default_version(self):
        return "0.1"

    def get_default_url(self):
        default = f"https://github.com/{self.github_username}"
        return default + f"/{self.name}"

    def get_default_author(self):
        return getpass.getuser()

    def get_default_email(self):
        return f"{getpass.getuser().lower()}@gmail.com"

    def get_default_keywords(self):
        default = f"{self.name}, "
        default += f"{self.author}, "
        return default + f"{self.github_username}, "

    def get_default_requirements(self):
        return "cleverdict, "

    def get_metadata(self):
        """
        Check config file for previous values.  If no value is set, prompts for
        a value and updates the relevant Package attribute.
        """
        prompts = {
            "version": "Please enter latest version number:",
            "url": "Please enter a link to the package repository:",
            "description": "Please enter a description with escape characters for \\ \" ' etc.:",
            "author": "Please enter the full name of the author:",
            "email": "Please enter an email address for the author:",
            "keywords": "Please enter some keywords separated by a comma:",
            "requirements": "Please enter any packages/modules that absolutely "
                            "need to be installed for yours to work, separated by commas:",
        }
        for key, prompt in prompts.items():
            default = self.get(key)
            if not default:
                try:
                    func = f"get_default_{key.lower()}"
                    default = getattr(self, func)()
                except AttributeError:
                    pass
            if key == "version" and self.get("version"):
                default = self.next_version
            new = sg.popup_get_text(prompt, default_text=default, **sg_kwargs)
            if new is None:
                break
            setattr(self, key, new)

    def get_classifiers(self):
        """
        Selects classifiers in key categories to better describe the package.
        Choices are imported from classifiers.classifier_list.

        .classifiers updated in place as a string of comma-separated values
        """
        classifiers = []
        for group in GROUP_CLASSIFIERS:
            choices = [x for x in classifier_list if x.startswith(group)]
            selection = self.__class__.prompt_with_checkboxes(group, choices)
            if selection is None:
                break
            if selection:
                classifiers.extend(selection)
        self.classifiers = ", ".join(classifiers)

    def get_license(self):
        """
        Select from a shortlist of common license types
        Choices are imported from license.licenses_dict.
        Updates made in place to .license
        """
        license_dict_path = Path(filename)
        if license_dict_path.is_file():
            with license_dict_path.open('r') as file:
                license_dict = json.load(file)
            licenses = [CleverDict(x) for x in license_dict]
        else:
            licenses = []
        layout = [[sg.Text(text="Please select a License for your package:")]]
        for pkg_license in licenses:
            layout.extend(
                [
                    [
                        sg.Radio(
                            pkg_license.key.upper(),
                            "licenses",
                            font="bold 12",
                            tooltip=pkg_license.description,
                            size=(10, 1),
                        ),
                        sg.Text(
                            text=pkg_license.html_url, enable_events=True, size=(40, 1)
                        ),
                    ]
                ]
            )
        layout += [[sg.Button("OK")]]
        window = sg.Window("easypypi", layout, size=(600, 400), resizable=True)
        while True:
            event, values = window.read(close=True)
            if event == "OK" and any(values.values()):
                window.close()
                self.setattr_direct("license_dict", [licenses[k] for k, v in values.items() if v][0])
                break
            if event:
                if "http" in event:
                    webbrowser.open(event)
            else:
                window.close()
                self.setattr_direct("license_dict", licenses[0])  # Default license
                print(f"\nDefault license selected: {self.license_dict.name}")
                break
        self.finalise_license()  # Creates .license

    def finalise_license(self):
        """
        Make simple updates based on license_dict.implementation instructions
        """
        year = str(datetime.datetime.now().year)
        replacements = dict()
        self.license_text = self.license_dict.body
        if self.license_dict.key == "lgpl-3.0":
            self.license_text += '\nThis license is an additional set of permissions to the ' \
                            '<a href="/licenses/gpl-3.0">GNU GPLv3</a> license which is reproduced below:\n\n'
            gpl = [CleverDict(x) for x in licenses_dict if x["key"] == "gpl-3.0"][0]
            self.license_text += gpl.body
        if self.license_dict.key == "mit":
            replacements = {"[year]": year, "[fullname]": self.author}
        if self.license_dict.key in ["gpl-3.0", "lgpl-3.0", "agpl-3.0"]:
            replacements = {
                "<year>": year,
                "<name of author>": self.author,
                "<program>": self.name,
                "Also add information on how to contact you by electronic and paper mail.": f"    Contact email: {self.email}",
                "<one line to give the program's name and a brief idea of what it does.>": f"{self.name}: {self.description}",
            }
        if self.license_dict.key == "apache-2.0":
            replacements = {"[yyyy]": year, "[name of copyright owner]": self.author}
        if replacements:
            for old, new in replacements.items():
                self.license_text = self.license_text.replace(old, new)

    def get_username(self, account):
        """ Multi-purpose function to prompt for Github/PyPI/Test PyPI username"""
        if not self.get(account + "username"):
            setattr(
                self,
                account + "username",
                sg.popup_get_text(
                    f'Please enter your {account.title().replace("_", " ").replace("pi", "PI")}username:',
                    default_text=self.get(account + "username") or self.get("github_username"),
                    **sg_kwargs,
                ),
            )

    def get_password(self, account):
        """
        Multi-purpose function to prompt for Github/PyPI/Test PyPI password

        account : pypi_, pypi_test_, or githhub_
        """
        if not self.get(f"{account}password"):
            setattr(
                self,
                f"{account}password",
                sg.popup_get_text(
                    f'Please enter your {account.title().replace("_", " ").replace("pi", "PI")}password '
                    f'(not saved to file):',
                    password_char="*",
                    default_text=self.get(account + "password"),
                    **sg_kwargs,
                ),
            )

    def check_account_credentials(self, filter=None):
        """
        Prompts for TestPyPI/PyPI account names for twine to use.

        This approach avoids the need for a .pypirc config file:
        https://packaging.python.org/specifications/pypirc/#common-configurations

        Creates the following attributes in place:

        .pypi_username
        .pypi_test_username
        .github_username
        .pypi_password
        .pypi_test_password
        .github_password

        filter : restricts the function to the account specified

        """
        url = r"https://pypi.org/account/register/"
        accounts = {
            "github_": ["Github", "https://github.com/join"],
            "pypi_": ["PyPI", url],
            "pypi_test_": ["Test PyPI", url.replace("pypi", "test.pypi")],
        }
        if filter:
            accounts = {k:v for k,v in accounts.items() if k == filter}
        for account, (repo, url) in accounts.items():
            if not self.get(account + "username"):
                response = sg.popup_yes_no(
                    f"Do you need to register for an account on {repo}?", **sg_kwargs)
                if response is None:
                    return
                if response == "Yes":
                    print(
                        f'\n⚠ Please create a {account.title().replace("_", " ")}account, '
                        f'then return to easyPyPI to continue the process...')
                    webbrowser.open(url)
                self.get_username(account)
            if not self.get(account + "password"):
                self.get_password(account)
        self.url = self.get_default_url()  # Uses self.github_username

    def copy_other_files(self):
        """
        Prompts for additional files to copy over into the newly created folder:
        \package_name\package_name
        """
        files = sg.popup_get_file(
            "Please select any other files to copy to new project folder",
            **sg_kwargs,
            default_path="",
            multiple_files=True,
        )
        if files is None:
            return
        for file in [Path(x) for x in files.split(";")]:
            new_file = self.setup_filepath / self.name / file.name
            if new_file.is_file():
                response = sg.popup_yes_no(
                    f"WARNING\n\n{file.name} already exists in\n{new_file.parent}\n\n Overwrite?",
                    **sg_kwargs,
                )
                if response == "No":
                    continue
            if file.is_file():
                shutil.copy(file, new_file)
                print(f"\n✓ Copied {file.name} to:\n {new_file.parent}")

    def update_script_lines(self):
        for keyword in self.__class__.setup_fields:
            old_line_starts = keyword.upper() + " = "
            if keyword == "license":
                new_value = self.license
            else:
                new_value = getattr(self, keyword)
            self.script_lines = update_line(
                self.script_lines, old_line_starts, new_value
            )

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
        # setup.py and LICENSE can be be overwritten as they're most likely to
        # be changed by user after publishing, and no code changes will be lost:
        self.update_script_lines()
        sfp = self.setup_filepath.parent

        # Create LICENSE:
        create_file(sfp / "LICENSE", self.license_text, overwrite=True)

        # Create setup.py:
        create_file(self.setup_filepath, self.script_lines, overwrite=True)

        # Other files are just bare-bones initially, imported from templates:
        templates = {"readme_template.md": sfp / "README.md",
                     "init_template.py": sfp / self.name / "__init__.py",
                     "script_template.py": sfp / self.name / (self.name + ".py"),
                     "test_template.py": sfp / self.name / ("test_" + self.name + ".py"), }

        # Read in, make replacements, create in new folder structure
        for template_filepath, destination_path in templates.items():
            template_filepath = self.easypypi_dirpath / template_filepath
            with open(template_filepath, "r") as file:
                text = file.read()
            for replacement in REPLACEMENTS:
                text = text.replace(replacement, eval(f"f'{replacement}'"))
            create_file(destination_path, text)

    def run_setup_py(self):
        """ Creates a .tar.gz distribution file with setup.py """
        try:
            import setuptools
            import twine
        except ImportError:
            print("\n> Installing setuptools and twine if not already present...")
            os.system('cmd /c "python -m pip install setuptools wheel twine"')
        os.chdir(self.setup_filepath.parent)
        print(f"\n> Running {self.setup_filepath / 'setup.py'}...")
        os.system('cmd /c "setup.py sdist"')

    def upload_with_twine(self):
        """ Uploads to PyPI or Test PyPI with twine """
        choice = sg.popup(
            f"Do you want to upload {self.name} to\nTest PyPI, or go FULLY PUBLIC on the real PyPI?\n",
            **sg_kwargs,
            custom_text=("Test PyPI", "PyPI"),
        )
        if not choice:
            return
        if choice == "PyPI":
            params = "pypi"
            account = "pypi_"
        if choice == "Test PyPI":
            params = "testpypi"
            account = "pypi_test_"
        params += f" dist/*-{self.version}.tar.gz "
        self.check_account_credentials(account)
        os.chdir(self.setup_filepath.parent)
        if os.system(
                f'cmd /c "python -m twine upload '
                f'--repository {params} '
                f'-u {getattr(self, f"{account}username")} '
                f'-p {getattr(self, f"{account}password")}"'
        ):
            # A return value of 1 (True) indicates an error
            print("\n⚠ Problem uploading with Twine; probably either:")
            print("   - An authentication issue.  Check your username and password?")
            print("   - Using an existing version number.  Try a new version number?")
        else:
            url = "https://"
            url += "" if choice == "PyPI" else "test."
            webbrowser.open(url + f"pypi.org/project/{self.name}")
            response = sg.popup_yes_no(
                "Fantastic! Your package should now be available in your webbrowser, "
                "although you might need to wait a few minutes before it registers as the 'latest' version.\n\n"
                "Do you want to install it now using pip?\n",
                **sg_kwargs,
            )
            if response == "Yes":
                print()
                if not os.system(
                        f'cmd /c "python -m pip install -i https://test.pypi.org/simple/ {self.name} --upgrade"'
                ):
                    # A return value of 1 indicates an error, 0 indicates success
                    print(
                        f"\nⓘ You can view your package's details using 'pip show {self.name}':\n"
                    )
                    os.system(f'cmd /c "pip show {self.name}"')

    def create_github_repository(self):
        """ Creates an empty repository on Github """
        choice = sg.popup_yes_no(
            f"Do you want to create a repository on Github?\n",
            **sg_kwargs, )
        if choice != "Yes":
            return
        if not (self.get("github_password") and self.get("github_username")):
            self.check_account_credentials()
        browser = mechanicalsoup.StatefulBrowser(
            soup_config={'features': 'lxml'},
            raise_on_404=True,
            user_agent='MyBot/0.1: mysite.example.com/bot_info',
        )
        browser.open("https://github.com/login")
        browser.select_form('#login form')
        browser["login"] = self.github_username
        browser["password"] = self.github_password
        resp = browser.submit_selected()
        browser.open("https://github.com/new")
        browser.select_form('form[action="/repositories"]')
        browser["repository[name]"] = self.name
        browser["repository[description]"] = self.description
        browser["repository[visibility]"] = "private"
        resp = browser.submit_selected()
        # browser.launch_browser()  # Local copy for debugging
        webbrowser.open(self.url)

    def upload_to_github(self):
        """ Uploads package to Github using Git"""
        commands = f"""
        git init
        git add *.*
        git commit -m "Committing version {self.version}"
        git branch -M main
        git remote add origin https://github.com/{self.github_username}/{self.name}.git
        git push -u origin main
        """
        choice = sg.popup_yes_no(
            f'Do you want to upload (Push) your package to Github?\n\n⚠ CAUTION - '
            f'Only recommended when creating your repository for the first time!  '
            f'This automation is will run the following commands:\n\n{commands}',
            **sg_kwargs, )
        if choice != "Yes":
            return
        os.chdir(self.setup_filepath.parent)
        for command in commands.splitlines()[1:]:  # Ignore first blank line
            if not os.system(f"cmd /c {command}"):
                # A return value of 1 indicates an error, 0 indicates success
                print(f"\nⓘ Your package is now online at:\n  {self.url}':\n")

    def __str__(self):
        output = self.info(as_str=True)
        return output.replace("CleverDict", type(self).__name__, 1)

    @property
    def next_version(self):
        """ Suggests next package version number based on simple schemas """
        decimal_version = decimal(str(self.version))
        try:
            _, digits, exponent = decimal_version.as_tuple()
            if exponent == 0:  # i.e. 0 decimal places:
                increment = "0.1"
            else:
                increment = "0.01"
            return str(decimal_version + decimal(increment))
        except dec.InvalidOperation:
            return f"{self.version}-new"

    @staticmethod
    def prompt_with_checkboxes(group, choices):
        """
        Creates a scrollable checkbox popup using PySimpleGui
        Returns a set of selected choices, or and empty set
        """
        prompt = [
            sg.Text(
                text=f"Please select any relevant classifiers in the {group.title()} group:"
            )
        ]
        layout = [[sg.Checkbox(text=choice)] for choice in choices]
        buttons = [sg.Button("Next")]
        event, checked = sg.Window(
            "easypypi",
            [
                prompt,
                [
                    sg.Column(
                        layout,
                        scrollable=True,
                        vertical_scroll_only=True,
                        size=(600, 300),
                    )
                ],
                buttons,
            ],
            size=(600, 400),
            resizable=True,
        ).read(close=True)
        if event == "Next":
            return [choices[k] for k, v in checked.items() if v]
        if event is None:
            return
