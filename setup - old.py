from pathlib import Path
from setuptools import setup, find_packages

HERE = Path(__file__).parent
NAME = "easypypi"
GITHUB_USERNAME = "Pfython"
VERSION = "1.18"
DESCRIPTION = "easyPyPI (Pronounced 'Easy Pie-Pea-Eye') is a quick, simple, one-size-fits-all solution for sharing your Python creations on the Python Package Index (PyPI) so others can just `pip install your_script` with no fuss."
LICENSE = "MIT License"
AUTHOR = "Peter Fison"
EMAIL = "peter@southwestlondon.tv"
URL = "https://github.com/Pfython/easypypi"
KEYWORDS = "easypypi, Peter Fison, Pfython, pip, package, publish, share, build, deploy, Python"
CLASSIFIERS = "Development Status :: 4 - Beta, Intended Audience :: Developers, Operating System :: OS Independent, Programming Language :: Python :: 3.6, Programming Language :: Python :: 3.7, Programming Language :: Python :: 3.8, Programming Language :: Python :: 3.9, Topic :: Software Development :: Build Tools, Topic :: Software Development :: Version Control :: Git, Topic :: System :: Archiving :: Packaging, Topic :: System :: Installation/Setup, Topic :: System :: Software Distribution, Topic :: Utilities"
REQUIREMENTS = "cleverdict, pysimplegui, click, requests, twine, mechanicalsoup"


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
