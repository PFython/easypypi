from pprint import pprint
import os
import datetime
import requests
import webbrowser
from cleverdict import CleverDict
import json
from pathlib import Path
from decimal import Decimal as decimal
import PySimpleGUI as sg

def create_file(filepath, content):
    """
    Create a backup if required, then create new file using writelines
    """
    if type(content) == str:
        content = content.splitlines()
    if filepath.is_file():
        backup = filepath.with_name(filepath.stem + "- old.py")
        if backup.is_file():
            os.remove(backup)
        filepath.rename(backup)
        print(f"Renamed {filepath.name} to {backup.name}")
    filepath.touch()
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
