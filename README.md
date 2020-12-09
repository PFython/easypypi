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
- Getting your **Test PyPI** and **PyPI** credentials mixed up

Enjoy!

# 1. QUICKSTART

    c:\> pip install easypypi

    >>> from easypypi import Package
    >>> package = Package()

    # or:
    >>> package = Package("script_name")

Then just follow the prompts to provide the information required to describe your package on **PyPI**.  No knowledge of `setuptools`, `twine`, or how to write a `setup.py` script required.

![](https://media.giphy.com/media/Nw8z2olm0nGHC/giphy.gif)

# 2. UPDATING YOUR PACKAGE

Once you've gone through the creation process fully (or even partially) you can start again by simply creating a new object with the same name, and `easyPyPI` will remember your previous answers.  For more precise control you can manually get and set all of the metadata used in `setup.py`, as well as your `twine` credentials.

Thanks to the magic of [`cleverdict`](https://github.com/pfython/cleverdict) you can use *either* `object.attribute` or `dictionary['key']` notation, whichever you prefer:

    >>> package['email'] = "new@name.com"
    >>> package['license_dict'].name
    'MIT License'
    >>> package.version = "2.0"
    >>> package.next_version
    '2.1'

Your last set of answers (except passwords) are stored in a JSON config file will be kept up to date automatically when you change values.  The location defaults to the recommended setting folder for your Operating System.

# 3. THE FOUR STEP PROCESS

Apart from the obvious `__init__` when you create your `Package`, there are four main methods or 'entry points' which you can invoke directly to step through the publishing process:

- `.load_defaults()`
- `.review()`
- `.generate()`
- `.upload()`

A quick read through the code in each of these entry points will help you get your head around the process flow and you'll see exactly what other functions are being called, and in what order.  Here's a quick summary...

## The `.load_defaults()` Entry Point

Whenever you create a new `Package` object or manually run this method

    >>> package.load_defaults()

`easyPyPI` will create attributes based your most recent answers stored in the JSON config file.  If it can find a previously created `setup.py` based on the name and root path you specify, it will use those values in preference.  That means you can make subsequent edits directly to your `setup.py` file if you prefer (as long as you keep the same basic format it derived from `setup_template.py`) and `easyPyPI` will pick out the key values next time you run this method or create a new object.

## The `.review()` Entry Point

When you call this method you'll be prompted for a whole load of metadata that describes your `Package`.  The good news though is that having done so once, it remembers your input for future updates other packages, so you shouldn't need to type in your email address and other details slavishly any more.

    >>> package.review()

`easyPyPI` will use existing values where it can, prompting you to confirm or edit them, and failing that (e.g. the very first time you run `easyPyPI`) it will try to make helpful suggestions to get you started.

## The `.generate()` Entry Point

Once you're happy with all your metadata and get into the cycle of publishing new versions of your code, this method does the job of upversioning your package, generating a new `setup.py` file and pulling everything together in a `tar.gz` file ready for uploading:

    >>> package.generate()

## The `.upload()` Entry Point

Finally, when you're  ready to upload your latest `Package` to **Test PyPI** or **PyPI**, just call:

    >>> package.upload()

# 4. OTHER FEATURES

Automatically generate the next version number for your `Package` (more schemas coming soon):

    >>> package.version = "1.1"
    >>> package.next_version
    '1.11'

When you use the `.review()` method `easyPyPI` will helpfully update the current version number for you.  If you want to prevent this happening, e.g. to overwrite a current draft you can do so like this:

    >>> package.upversioned_already = True
    >>> package.generate()

    # Resets to False after going through the .review process

To find where easyPyPI and its default templates were installed:

    >>> package.easypypi_dirpath

To find the location of your JSON config file to manually inspect,  edit, or `os.remove()` it:

    >>> package.config_path
    # This should be under the default Settings folder for your Operating System.

To locate your package's setup.py:

    >>> package.setup_filepath

If you have extra files which you want to copy into the new folder structure, including the main script file you might have already created before deciding to make it into a package:

    >>> package.copy_other_files()

To see what else you can play with using your `Package` object:

    >>> package.keys()
    # You can then get/set values using object.attribute or dictionary['key'] notation

# 5. CONTRIBUTING
This is the author's first open source project and any help is welcome!

This may not be the *best* way of doing things, but if you'd like to get involved, please:

- Say hello to us on [Twitter](https://twitter.com/appawsom) or the [Pythonista Cafe](https://www.pythonistacafe.com/) initially so we can "put a face to the name".
- Fork this repository. Also STAR this repository for bonus karma!
- Create new branches with the following standardised names as required:

    - **cosmetic**: for reformatting and changes to comments, README, or user input/output e.g. print(), input() and GUI.
    - **enhancements**: for new features and extensions to old features
    - **refactoring**: for better ways to code existing features
    - **tests**: for new or better test cases
    - **bugfix**: for solutions to existing issues
    - **miscellaneous**: for anything else
- Create a separate `test_xyz.py` script for any coding changes, and document your tests (and any new code) clearly enough that they'll tell us everything we need to know about your rationale and implementation approach.
- When you're ready and any new code passes all your/our tests, create a Pull Request from one of your branches (above) back to the main branch of this repository.

If you'd be kind enough to follow that approach we think it'll help speed things on their way and cause less brain-ache all round. Thank you, and I can't wait to hear your thoughts!

# 6. PAYING IT FORWARD


If `easyPyPI` helps you save time and focus on more important things, please feel free to to show your appreciation by starring the repository on Github.

I'd also be delighted if you wanted to:

<a href="https://www.buymeacoffee.com/pfython" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/arial-yellow.png" alt="Buy Me A Coffee" width="217px" ></a>


