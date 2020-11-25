"""
Functions shared by easypypi.py and licenses.py
"""

import os

def create_file(filepath, content, **kwargs):
    """
    Create a backup if required, then create new file using writelines
    Returns "file exists" if filepath already exists and overwrite = False
    """
    if type(content) == str:
        content = content.splitlines()
    if filepath.is_file():
        if kwargs.get("overwrite"):
            backup = filepath.with_name(filepath.stem + " - old.py")
            if backup.is_file():
                os.remove(backup)
            filepath.rename(backup)
            print(f"Renamed {filepath.name} to {backup.name}")
            filepath.touch()  # Create empty file to append lines to
        else:
            print(f"Existing file preserved: {filepath}")
            return "file exists"
    with open(filepath, "a") as file:
        file.writelines(content)
        print(f"Created new file {filepath}")

def update_line(script, old_line_starts, new_line):
    """ Updates and returns, ready for writing to setup.py """
    for index, line in enumerate(script.copy()):
        if line.lstrip().startswith(old_line_starts):
            if not new_line.startswith("["):
                new_line = f'"{new_line}"'
            script[index] = old_line_starts + new_line +"\n"
            print(f"Updated script line {index+1}:\n{script[index][:500]}")
            break  # only update first occurrence
    return script
