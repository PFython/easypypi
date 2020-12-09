import json
from json import JSONDecodeError
from pathlib import Path

import requests

filename = str(Path(__file__).parent / 'licenses.json')


def fetch_license_data():
    """
    Uses Github  API to fetch basic information about popular license choices
    Rate limited to 60 queries per hour (unauthenticated).
    """
    api_links = {
        "MIT": "https://api.github.com/licenses/mit",
        "GPL": "https://api.github.com/licenses/gpl-3.0",
        "LGPL": "https://api.github.com/licenses/lgpl-3.0",
        "MPL": "https://api.github.com/licenses/mpl-2.0",
        "AGPL": "https://api.github.com/licenses/agpl-3.0",
        "Apache": "https://api.github.com/licenses/apache-2.0",
        "Unlicense": "https://api.github.com/licenses/unlicense",
    }
    licenses = [requests.get(api_link).json()
                for api_link in api_links.values()]
    return licenses


if __name__ == "__main__":
    """
    When run rather than imported, fetches the latest data for popluar software
    licenses and updates this script, starting "licenses_dict = ".

    licenses.json is imported by the main module easypypi.py
    """
    HERE = Path(filename).parent
    # print(f"{filename} located in {HERE}")
    file = Path(filename)
    valid_json = True

    try:
        json.load(file.open('r'))
    except JSONDecodeError:
        valid_json = False

    if file.exists() and valid_json:
        print(f"\nⓘ Existing file preserved:\n  {file}")
    else:
        with file.open('w') as file:
            json.dump(fetch_license_data(), file)
        print(f"\n✓ Created new file:\n  {file}")
