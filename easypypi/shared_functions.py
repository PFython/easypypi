"""
Functions shared by easypypi.py and licenses.py
Check: Separate file required to avoid circular import?
"""

import os


def create_file(filepath, content, **kwargs):
    """
    Create a new file using writelines, and backup if filepath==setup.py.
    Returns "file exists" if filepath already exists and overwrite = False
    """
    if isinstance(content, str):
        content = content.splitlines(True)  # keep line breaks
    if filepath.is_file():
        if kwargs.get("overwrite"):
            if filepath.name == "setup.py":
                backup = filepath.with_name(f"{filepath.stem} - old.py")
                filepath.replace(backup)
                print(f"\n✓ Renamed {filepath.name} to:\n  {backup.name}")
            else:
                os.remove(filepath)
        else:
            print(f"\nⓘ Existing file preserved:\n  {filepath}")
            return "file exists"
    with filepath.open("a") as file:
        file.writelines(content)
        print(f"\n✓ Created new file:\n  {filepath}")


def update_line(script_lines, old_line_starts, new_value):
    """ Updates and returns script_lines, ready for writing to setup.py """
    for index, line in enumerate(script_lines.copy()):
        if line.lstrip().startswith(old_line_starts):
            try:
                if isinstance(new_value, list):
                    # Add quotation marks unless list
                    new_value = ", ".join(new_value)
                else:
                    new_value = f'"{new_value}"'
                old_line = script_lines[index]
                script_lines[index] = old_line_starts + new_value.rstrip() + "\n"
                if old_line != script_lines[index]:
                    print(
                        f"\n✓ Updated script line {index + 1}:\n{script_lines[index].rstrip()[:400]}"
                    )
                break  # only update first occurrence
            except (IndexError, TypeError):
                print(new_value, type(new_value))
    return script_lines
