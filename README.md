# `easyPyPI`
![](https://github.com/PFython/easypypi/blob/main/easypypi.png?raw=true)
`easyPyPI` (Pronounced "Easy Pie-Pea-Eye") is a quick, simple, one-size-fits-all solution for sharing your Python creations on the [Python Package Index](https://pypi.org/) (**PyPI**) so others can just `pip install your_script` with no fuss.

`easyPyPI` is mainly intended for Pythonistas who've been put off publishing to **PyPI** before now or tried it but, like the author (pictured below) thought:

> "*There **must** be an easier way to do this!*"

![](https://media.giphy.com/media/XIqCQx02E1U9W/giphy.gif)

Well now there is.  Just install `easyPyPI`, run it, and follow the prompts.  No knowledge of `setuptools`, `twine`, or how to write a `setup.py` script required.

    pip install easypypi
    python.exe -m easypypi

With `easyPyPI` you don't have to spend hours...

- Reading tutorials about `distutils` only to realise `setuptools` is what you need.
- Reading yet more tutorials just to work out the essential steps (below).
- Manually creating a folder structure and moving your script(s) there.
- Manually creating a skeleton `README.md`
- Manually creating a skeleton `__init__.py`
- Manually creating a skeleton `test_yourscript.py`
- Manually creating and updating a `LICENSE`
- Manually creating a `setup.py` script and wondering what on earth to put in it
- Remembering to update your Version number each time you publish
- Running `setup.py` in just the right way to create your distribution files
- Installing and running `twine` in just the right way to upload your package to **Test PyPI** then **PyPI**
- Setting environment variables or creating a `.pypirc` file for `twine`  to use

Enjoy!


![](https://media.giphy.com/media/Nw8z2olm0nGHC/giphy.gif)

### UNDER THE BONNET

If you want a bit more control and understanding of what's going on, the main `easyPyPI` class is called `Package` and we've included two main entry points which will help you get your head around the process flow:

- `start_new_package()`
- `update_existing_package()`

Have a look at those functions inside `easypypi.py` and it should be fairly easy to see what other functions are being used, and in what order.

If you want to play around in your IDE here are some ideas to get you started:

```
>>> from easypypi import start, update, version

# Create a new package object:
>>> package  = start()

# Check if any required information is missing:
>>> package.review_metadata()

# Upversion and republish a package previously created using easyPyPI:
>>> package = update(package)

# Suggest the next version number (more schemas coming soon):
>>> version("1.1")
'1.11'

# Locate your easyPyPI config file:
>>> Package.config_path  # It's a class variable so capital 'P'

# Find where easyPyPI and its default templates were installed:
>>> package.easypypi_path  # or just:
>>> HERE

# Locate your package's setup.py:
>>> package.setup_path

# If you have files in different locations which you want to include:
>>> package.copy_other_files()
```




If `easyPyPI` helps save you some time so you can focus on more important things in life, please feel free to to show your appreciation and:

<a href="https://www.buymeacoffee.com/pfython" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/arial-yellow.png" alt="Buy Me A Coffee" width="217px" ></a>


