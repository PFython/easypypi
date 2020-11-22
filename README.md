# `easyPyPI`
- Want to share your Python script(s)  so others can simply `pip install yourscript`?
- Daunted by the numerous/tedious tutorials for `distutils`, `setuptools` and the [Python Package Index](https://pypi.org/) (**PyPI**)?

`easyPyPI` is a simple, one-size-fits-all solution that caters for 87.3% of use cases (*Ed - really?!!*).  It's aimed at Pythonistas who've never published to **PyPI** or have, but thought "There *must* be an easier way than this!".

![Before](https://media.giphy.com/media/XIqCQx02E1U9W/giphy.gif)

Well now there is.  Just install `easyPyPI`, import it, and follow the prompts.  No knowledge of `setuptools`, `twine`, or how to write a `setup.py` script required.

    pip install easypypi
    
    >>> import easypypi
    
With `easyPyPI` you no longer have to:

- Manually create a folder structure and move your script there.
- Manually create a skeleton `README.md`
- Manually create a skeleton `__init__.py`
- Manually create a skeleton `test_yourscript.py`
- Manually create a `LICENSE` using the Github Licenses API
- Manually create `setup.py` file based
- Remember to update your Version number each time
- Run `setup.py` in the recommended way to create a distribution file
- Install and run `twine` to upload your distribution file to **Test PyPI** / **PyPI**
- Remember to delete old distribution files

![After](https://media.giphy.com/media/Nw8z2olm0nGHC/giphy.gif)

*FOOTNOTE: It took me 3 years to realise I was pronouncing **PyPI** wrong!  It's as easy as: "Pie-Pea-Eye" in case you didn't know.  And why should you?*

