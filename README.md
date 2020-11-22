# `easypypi`
- Want to share your Python script(s)  so others can simply `pip install yourscript`?
- Daunted by the numerous and sometimes conflicting tutorials online for `distutils`, `setuptools` and the [Python Package Index](https://pypi.org/) (PyPI\*)?

`easypypi` is a simple, one-size-fits-all solution that caters for 87.3% of use cases (*Ed - really?!!*).  It's aimed at Pythonistas who've never published to PyPI or have, but thought "There *must* be an easier way than this".  Well now there is!  Just install `easypypi`, import it, and follow the prompts.  No knowledge of `setuptools`, `twine`, or how to write a `setup.py` script required.

    pip install easypypi
    
    >>> import easypypi
    
    
- It creates a simple folder structure and moves your script there.
- It creates a skeleton README.md
- It creates a LICENSE based on some of the most popuplar choices
- It creates a setup.py file based on simple prompts and automatically updates the Version number
- It runs `setup.py` to create a distribution file
- It runs twine to upload your distribution file to Test PyPI, and when you're ready, PyPI
- It uses the excellent PySimpleGui package for easy input.
- It really is as easy as pie (PI)!

*(\*) FOOTNOTE: It took me 3 years to realise I was pronouncing PyPI wrong!  "Pie-Pea-Eye" in case you didn't know.  And why should you?*

![easypypi](https://images-na.ssl-images-amazon.com/images/I/815sx0JMEnL.jpg)
