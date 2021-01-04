import json
from json import JSONDecodeError
from pathlib import Path
from cleverdict import CleverDict

import requests

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
        "Boost": "https://api.github.com/licenses/bsl-1.0",
    }
    licenses = [requests.get(api_link).json()
                for api_link in api_links.values()]
    return licenses

def load_licenses_json():
    """
    Loads license metadata from licenses.json and converts each license to
    a cleverdict.

    Returns: List of 8 cleverdicts, one for each main license type
    """
    license_dict_path = Path(LICENSES_FILENAME)
    if license_dict_path.is_file():
        with license_dict_path.open('r') as file:
            license_dict = json.load(file)
        return [CleverDict(x) for x in license_dict]
    else:
        return []

LICENSES_FILENAME = str(Path(__file__).parent / 'licenses.json')
LICENSE_NAMES = {'MIT': 'MIT License',
                 'GPL-3.0': 'GNU General Public License v3 (GPLv3)',
                 'LGPL-3.0': 'GNU Lesser General Public License v3 (LGPLv3)',
                 'MPL-2.0': 'Mozilla Public License 2.0 (MPL 2.0)',
                 'AGPL-3.0': 'GNU Affero General Public License v3',
                 'Apache-2.0': 'Apache Software License',
                 'Unlicense': 'The Unlicense (Unlicense)',
                 'BSL-1.0': 'Boost Software License 1.0 (BSL-1.0)',}
# Key: spdx_id from JSON
# Value: PyPI license name under 'License :: OSI Approved ::'
LICENSES = load_licenses_json()

if __name__ == "__main__":
    """
    When run rather than imported, fetches the latest data for popluar software
    licenses and updates this script, starting "licenses_dict = ".

    licenses.json is imported by the main module easypypi.py
    """
    HERE = Path(LICENSES_FILENAME).parent
    file = Path(LICENSES_FILENAME)
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
