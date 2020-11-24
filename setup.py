import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent
PACKAGE_NAME = ""
GITHUB_ID = ""
VERSION = 0
DESCRIPTION = ""
LICENSE = ""
AUTHOR = ""
EMAIL = ""
KEYWORDS = []
CLASSIFIERS = []
URL = ""
REQUIREMENTS = []

if __name__ == "__main__":
    setup(name = PACKAGE_NAME,
        packages = find_packages(),
        version = VERSION,
        license=LICENSE,
        description = DESCRIPTION,
        long_description=(HERE / "README.md").read_text(),
        long_description_content_type="text/markdown",
        author = AUTHOR,
        author_email = EMAIL,
        url = URL,
        download_url = f'{URL}/archive/{VERSION}.tar.gz',
        keywords = [x.strip() for x in KEYWORDS.split(",")],
        install_requires = [x.strip() for x in REQUIREMENTS.split(",")],
        classifiers = CLASSIFIERS,)



