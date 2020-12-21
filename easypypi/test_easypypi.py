# Tests for easypypi
import pytest
from easypypi import Package, keyring

class Test_First_Time_Use:
    def test_defaults(self):
        """ Check default values and derived defaults are conformant """
        package = Package()
        #
        # Parent folder generates from name not memory
        # Parent folder doesn't end with package name
        # Don't prompt for Github password until needed
        # Version number 0.1 for new packages
        # Github push prompt only at creation

    def test_Test_PyPI_credentials(self):
        """
        upload_with_twine should prompt for username & password if it can't
        find them in `keyring`
        """
        # Setup: Click OK to select default parent folder
        package = Package("test", _break = True)
        account = "Test_PyPI"
        # 1st Run: Select Test PyPI and enter "testuser" then "testpw"
        try:
            package.upload_with_twine()
        # Expected error: "Cannot find file (or expand pattern)"
        assert self.Test_PyPI_username == "testuser"
        assert self.Test_PyPI_password == "testpw"
        assert keyring.get_password(account, getattr(self, account+"_username")) == "testpw"
        # 2nd Run:  Select Test PyPI.  Should return without prompts.
        package.upload_with_twine()
        assert self.Test_PyPI_username == "testuser"
        assert self.Test_PyPI_password == "testpw"
        assert keyring.get_password(account, getattr(self, account+"_username")) == "testpw"
        # Breakdown: Get a copy of username before deleting:
        username = getattr(package, f"{account}_username")
        package.delete_credentials(account)
        assert not hasattr(package, f"{account}_username")
        assert not hasattr(package, f"{account}_password")
        assert not keyring.get_password(account, username)

    def test_PyPI_credentials(self):
        """
        upload_with_twine should prompt for username & password if it can't
        find them in `keyring`
        """
        # Setup: Click OK to select default parent folder
        package = Package("test", _break = True)
        account = "PyPI"
        # 1st Run: Select Test PyPI and enter "testuser" then "testpw"
        try:
            package.upload_with_twine()
        except InvalidDistribution:
            print("Expected error: Cannot find file (or expand pattern)"
        assert self.PyPI_username == "testuser"
        assert self.PyPI_password == "testpw"
        assert keyring.get_password(account, getattr(self, account+"_username")) == "testpw"
        # 2nd Run:  Select Test PyPI.  Should return without prompts.
        package.upload_with_twine()
        assert self.Test_PyPI_username == "testuser"
        assert self.Test_PyPI_password == "testpw"
        assert keyring.get_password(account, getattr(self, account+"_username")) == "testpw"
        # Breakdown: Get a copy of username before deleting:
        username = getattr(package, f"{account}_username")
        package.delete_credentials(account)
        assert not hasattr(package, f"{account}_username")
        assert not hasattr(package, f"{account}_password")
        assert not keyring.get_password(account, username)
