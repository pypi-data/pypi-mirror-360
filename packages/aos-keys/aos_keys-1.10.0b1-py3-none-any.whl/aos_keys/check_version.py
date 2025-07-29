#
#  Copyright (c) 2018-2025 EPAM Systems Inc.
#
import json
import os
import time

import requests
from aos_keys.common import print_error, print_message
from appdirs import user_cache_dir

try:
    from importlib.metadata import version
except ImportError:
    from importlib_metadata import version

from packaging.version import Version

DOCS_URL = 'https://docs.aosedge.tech/docs/quick-start/set-up/'
GET_TIMEOUT = 30
CACHE_EXPIRY = 3600  # 1 hour in seconds


def get_cached_response(package_name):
    cache_file = os.path.join(user_cache_dir(package_name), f'{package_name}_pypi_cache.json')

    try:
        if not os.path.exists(cache_file):
            return None

        with open(cache_file, 'r', encoding='utf-8') as file_content:
            cache_data = json.load(file_content)

        # Check if cache is expired
        if time.time() - cache_data['timestamp'] > CACHE_EXPIRY:
            return None

        return cache_data['response']
    except (IOError, json.JSONDecodeError):
        return None


def save_cache_response(package_name, response_data):
    try:
        if not os.path.exists(user_cache_dir(package_name)):
            os.makedirs(user_cache_dir(package_name), exist_ok=True)

        cache_file = os.path.join(user_cache_dir(package_name), f'{package_name}_pypi_cache.json')
        cache_data = {
            'timestamp': time.time(),
            'response': response_data,
        }

        with open(cache_file, 'w', encoding='utf-8') as file_content:
            json.dump(cache_data, file_content)
    except OSError:
        # If we can't save the cache, just continue without caching
        pass  # noqa: WPS420


def clean_cache_response(package_name):
    try:
        if os.path.exists(user_cache_dir(package_name)):
            cache_file = os.path.join(user_cache_dir(package_name), f'{package_name}_pypi_cache.json')
            os.remove(cache_file)
    except OSError:
        # If we can't save the cache, just continue without caching
        pass  # noqa: WPS420


def check_latest_version(package_name):
    installed_version = Version(version(package_name))

    # Try to get cached response first
    resp_json = get_cached_response(package_name)

    if resp_json is None:
        # No valid cache, fetch from PyPI
        pypi_url = f'https://pypi.org/pypi/{package_name}/json'
        try:
            response = requests.get(
                url=pypi_url,
                timeout=GET_TIMEOUT,
            )
            response.raise_for_status()
            resp_json = response.json()
            # Save the response to cache
            save_cache_response(package_name, resp_json)
        except requests.exceptions.RequestException:
            print_message(
                '[yellow]Cannot get latest version of package. Check your internet connection and try again later.',
            )
            return

    if installed_version.is_prerelease and resp_json.get('releases'):
        latest_version = max(Version(ver) for ver in resp_json.get('releases').keys())
    else:
        latest_version = Version(resp_json.get('info', {}).get('version', '0.0.0'))

    if max(installed_version, latest_version) == installed_version:
        return

    if installed_version.major != latest_version.major or installed_version.minor != latest_version.minor:
        print_error(
            f'[red]{package_name} installed: {installed_version} latest: {latest_version} have to be updated',
        )
    else:
        print_message(
            f'[yellow]{package_name} installed: {installed_version} latest: {latest_version} need to be updated',
        )
    print_message(f'Perform updating package according to AosEdge documentation: {DOCS_URL}')
