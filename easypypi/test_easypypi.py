# Tests for easypypi
import pytest
from easypypi.easypypi import *

sg.change_look_and_feel("DarkAmber")

def backup_config():
    """
    Backs up current config file then deletes it to simulute first time use
    """
    global backup_filepath, kwargs_backup
    kwargs_backup = sg_kwargs.copy()
    if sg_kwargs.get("title"):
        del sg_kwargs['title']
    backup_filepath = Package.config_filepath.with_name("config_backup.json")
    try:
        Package.config_filepath.replace(backup_filepath)
        print(f"\n ⓘ  config.json moved to {backup_filepath}")
    except FileNotFoundError:
        print(f"\n ⓘ  {Package.config_filepath} doesn't exist yet - no backup required.")

def restore_config():
    """ Restores previously copied config file """
    global sg_kwargs
    sg_kwargs = kwargs_backup.copy()
    backup_filepath.replace(Package.config_filepath)
    print("\n ⓘ  Original config.json restored.")

def notify(prompt):
    """ Popup an auto-close notification with instructions about a test """
    sg.popup_auto_close(prompt, title = "Testing", **sg_kwargs, auto_close_duration=8)

def check_credentials(package, account):
    assert getattr(package, f"{account}_username") == "testuser"
    assert getattr(package, f"{account}_password") == "testpw"
    assert keyring.get_password(account, getattr(package, account+"_username")) == "testpw"

def breakdown_credentials(package, account):
    """ Deletes username/password attributes and removes from keyring """
    # Get a copy of username before deleting:
    username = getattr(package, f"{account}_username")
    package.delete_credentials(account)
    assert not hasattr(package, f"{account}_username")
    assert not hasattr(package, f"{account}_password")
    assert not keyring.get_password(account, username)

class Test_First_Time_Use:
    def test_defaults(self):
        """ Check initial default values are conformant """
        backup_config()
        notify("When prompted, please click OK twice to select\nthe default NAME and PARENT FOLDER...")
        package = Package(_break = True)
        assert package.name == "as_easy_as_pie"
        assert package.version == "0.1"
        assert len(package.script_lines) == 47 # Depends on setup_template.py
        assert package.setup_filepath_str.endswith("setup.py")
        assert sorted(package.get_aliases()) == ['name', 'script_lines', 'setup_filepath_str', 'version']
        restore_config()

    def test_defaults_with_name(self):
        """ Check initial default values when name is supplied as argument """
        backup_config()
        notify("When prompted, click OK once\nto select the default PARENT FOLDER...")
        package = Package("test", _break = True)
        assert package.name == "test"
        assert package.version == "0.1"
        assert len(package.script_lines) == 47 # Depends on setup_template.py
        assert package.setup_filepath_str.endswith("setup.py")
        assert sorted(package.get_aliases()) == ['name', 'script_lines', 'setup_filepath_str', 'version']
        restore_config()

    def test_defaults_values(self):
        """ Check derived default values. """
        backup_config()
        notify("When prompted, click OK once\nto select the default PARENT FOLDER...")
        package = Package("test", _break = True)
        assert package.get_default_version() == "0.1"
        package.Github_username = "testuser"
        assert package.get_default_url() == 'https://github.com/testuser/test'
        assert package.name in package.get_default_keywords()
        assert package.author in package.get_default_keywords()
        assert package.Github_username in package.get_default_keywords()
        assert "cleverdict" in package.get_default_requirements()
        restore_config()

    def test_Test_PyPI_credentials(self):
        """
        upload_with_twine should prompt for username & password if it can't
        find them in `keyring`
        """
        backup_config()
        notify("When prompted, click OK once\nto select the default PARENT FOLDER...")
        package = Package("test", _break = True)
        notify(f"1st Run: Click the 'Test PyPI' button then enter:\n'testuser' and 'testpw' for username and password")
        package.upload_with_twine()
        notify(f"Expected error:\n\nCannot find file (or expand pattern): ...")
        check_credentials(package, "Test_PyPI")
        notify(f"2nd Run:  Click the 'Test PyPI' button.\n\nYou shouldn't need to re-enter username or password")
        package.upload_with_twine()
        breakdown_credentials(package, "Test_PyPI")
        restore_config()

    def test_PyPI_credentials(self):
        """
        upload_with_twine should prompt for username & password if it can't
        find them in `keyring`
        """
        backup_config()
        notify("When prompted, click OK once\nto select the default PARENT FOLDER...")
        package = Package("test", _break = True)
        notify(f"1st Run: Click the 'PyPI' button then enter:\n'testuser' and 'testpw' for username and password")
        package.upload_with_twine()
        notify(f"Expected error:\n\nCannot find file (or expand pattern): ...")
        check_credentials(package, "PyPI")
        notify(f"2nd Run:  Click the 'PyPI' button.\n\nYou shouldn't need to re-enter username or password")
        package.upload_with_twine()
        breakdown_credentials(package, "PyPI")
        restore_config()

    def test_Github_credentials(self):
        """
        upload_with_twine should prompt for username & password if it can't
        find them in `keyring`
        """
        backup_config()
        notify("When prompted, click OK once\nto select the default PARENT FOLDER...")
        package = Package("test", _break = True)
        package.url = "https://github.com/PFython/easypypi"
        notify(f"1st Run: Click the 'Yes' button then enter:\n'testuser' and 'testpw' for username and password")
        try:
            package.create_github_repository()
        except LinkNotFoundError:
            notify(f"Expected error - not real login credentials")
        check_credentials(package, account)
        notify(f"2nd Run:  Click the 'Yes' button.\n\nYou shouldn't need to re-enter username or password")
        try:
            package.create_github_repository()
        except LinkNotFoundError:
            notify(f"Expected error - not real login credentials")
        breakdown_credentials(package, "Github")
        restore_config()

    def test_load_defaults(self):
        """ Tests the Entry Point: load_defaults() """
        # Requires an existing setup.py file
        # Should NOT prompt for name again?
        # Check for creation of package folder

    def test_review(self):
        """ Tests the Entry Point: review() """
        pass

    def test_generate(self):
        """ Tests the Entry Point: generate() """
        pass

    def test_upload(self):
        """ Tests the Entry Point: upload() """
        pass


