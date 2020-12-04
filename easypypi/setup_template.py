from pathlib import Path
from setuptools import setup, find_packages

HERE = Path(__file__).parent
PACKAGE_NAME = ""
GITHUB_ID = ""
VERSION = 0
DESCRIPTION = ""
LICENSE = ""
AUTHOR = ""
EMAIL = ""
URL = ""
KEYWORDS = ""
CLASSIFIERS = ""
REQUIREMENTS = ""

def comma_split(text: str):
    """
    Returns a list of strings after splitting original string by commas
    Applied to KEYWORDS, CLASSIFIERS, and REQUIREMENTS
    """
    return [x.strip() for x in text.split(",")]

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
        keywords = comma_split(KEYWORDS),
        install_requires = comma_split(REQUIREMENTS),
        classifiers = comma_split(CLASSIFIERS),)



