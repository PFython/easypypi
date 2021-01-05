# Auto-generated by easyPyPI: https://github.com/PFython/easypypi
# Preserve current formatting to ensure easyPyPI compatibility.

from pathlib import Path
from setuptools import find_packages
from setuptools import setup

HERE = Path(__file__).parent
NAME = "easypypi"
GITHUB_USERNAME = "Pfython"
VERSION = "2.0.1"
DESCRIPTION = "easyPyPI is THE easiest and quickest way to publish your Python creations on the Python Package Index (PyPI) so other people can just `pip install your_script`."
LICENSE = "MIT License"
AUTHOR = "Peter Fison"
EMAIL = "peter@southwestlondon.tv"
URL = "https://github.com/Pfython/easypypi"
KEYWORDS = "easypypi, Peter Fison, Pfython, pip, package, publish, share, build, deploy, Python"
CLASSIFIERS = "Development Status :: 5 - Production/Stable, Intended Audience :: Developers, Operating System :: OS Independent, Programming Language :: Python :: 3.6, Programming Language :: Python :: 3.7, Programming Language :: Python :: 3.8, Programming Language :: Python :: 3.9, Topic :: Software Development :: Build Tools, Topic :: Software Development :: Libraries :: Python Modules, Topic :: Software Development :: Libraries :: pygame, Topic :: Software Development :: Version Control :: Git, Topic :: System :: Archiving :: Packaging, Topic :: Utilities, License :: OSI Approved :: MIT License"
REQUIREMENTS = "cleverdict, pysimplegui, click, twine, keyring, mechanicalsoup, pep440_version_utils"


def comma_split(text: str):
    """
    Returns a list of strings after splitting original string by commas
    Applied to KEYWORDS, CLASSIFIERS, and REQUIREMENTS
    """
    if type(text) == list:
        return [x.strip() for x in text]
    return [x.strip() for x in text.split(",")]


if __name__ == "__main__":
    setup(name=NAME,
          packages=find_packages(),
          version=VERSION,
          license=LICENSE,
          description=DESCRIPTION,
          long_description=(HERE / "README.md").read_text(),
          long_description_content_type="text/markdown",
          author=AUTHOR,
          author_email=EMAIL,
          url=URL,
          download_url=f'{URL}/archive/{VERSION}.tar.gz',
          keywords=comma_split(KEYWORDS),
          install_requires=comma_split(REQUIREMENTS),
          classifiers=comma_split(CLASSIFIERS), )
