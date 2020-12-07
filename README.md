# `easyPyPI`
![](https://github.com/PFython/easypypi/blob/main/easypypi.png?raw=true)
`easyPyPI` (Pronounced "Easy Pie-Pea-Eye") is a quick, simple, one-size-fits-all solution for sharing your Python creations on the [Python Package Index](https://pypi.org/) (**PyPI**) so others can just `pip install your_script` with no fuss.

`easyPyPI` is mainly intended for Pythonistas who've been put off publishing to **PyPI** before now or tried it but, like the author (pictured below) thought:

> "*There **must** be an easier way to do this!*"

![](https://media.giphy.com/media/XIqCQx02E1U9W/giphy.gif)

Well now there is!  With `easyPyPI` you don't have to spend hours...

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

### QUICKSTART

    c:\> pip install easypypi

    >>> from easypypi import Package
    >>> package = Package()

Then just follow the prompts to provide the information required to describe your package on **PyPI**.  No knowledge of `setuptools`, `twine`, or how to write a `setup.py` script required.

![](https://media.giphy.com/media/Nw8z2olm0nGHC/giphy.gif)

### FURTHER OPTIONS

Once you've gone through the process once and created a `Package` object, you can then get and set all of the metadata used in `setup.py`, as well as your `twine` credentials using *either* `object.attribute` or `dictionary['key']` notation, thanks to the magic of `cleverdict`:

    >>> package.license.name
    'MIT License'
    >>> package['email'] = "new@name.com"

And thanks again to `cleverdict` your information (except passwords) will automatically save to a JSON config file that update dynamically when you change any metadata values in this way.  To automatically upversion your package, create a new `setup.py` file and a new `tar.gz` file ready for uploading, just type:

    >>> package.update_files()

Then to actually upload to **Test PyPI** or **PyPI**:

    >>> package.upload()

If you want restart and use the prompts to supply different metadata, just:

    >>> package.start()

### UNDER THE BONNET

If you want a bit more control and understanding of what's going on 'under the bonnet', we've included three main entry points which you can call directly.  A quick read through these methods will help you get your head around the process flow and you'll see what other functions are being used, and in what order.

- `Package.start()`
- `Package.update_files()`
- `Package.upload()`

If you want to play around in your IDE here are some ideas to get you started...

Import some shortcuts:

    >>> from easypypi import start, update, upload, version

Check if any required information is missing:

    >>> package.review_metadata()

Suggest the next version number (more schemas coming soon):

    >>> upversion("1.1")
    '1.11'

Prevent upversioning when creating new files:

    >>> package.upversioned_already = True
    >>> package.update()

    # Resets to False after going through the .start process

Find where easyPyPI and its default templates were installed:

    >>> package.easypypi_path

Find the location of your JSON config file to manually inspect or edit it:

    >>> package.config_path
    # This should be under the default Settings folder for your Operating System.

Locate your package's setup.py:

    >>> package.setup_path

If you have files in different locations which you want to include:

    >>> package.copy_other_files()


List all the dictionary keys of you package object:

    >>> package.keys()
    # You can then get/set values using object.attribute or dictionary['key'] notation

### ENJOY !


If `easyPyPI` helps save you some time so you can focus on more important things in life, please feel free to to show your appreciation by starring the repository on Github. I'd also be delighted if you felt the urge to:

<a href="https://www.buymeacoffee.com/pfython" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/arial-yellow.png" alt="Buy Me A Coffee" width="217px" ></a>


