#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
from typing import Any, Union

import requests
from packaging.version import InvalidVersion
from packaging.version import Version as Version_parse
from packaging.version import parse as parse_version

from slpkg.config import config_load
from slpkg.views.version import Version

# Constants for the script
CHANGELOG_URL = 'https://gitlab.com/dslackw/slpkg/-/raw/master/CHANGELOG.md'
VERSION_PREFIX = '##'  # The prefix used for version lines in the ChangeLog file


def get_installed_version() -> str:
    """
    Retrieves the locally installed version of the software.
    Assumes the 'Version' class is available and functional.
    If 'Version' is not found, it logs an error and returns a default low version.
    """
    try:
        # Replace this with your actual method to get the installed version.
        # For example, if you have a __version__ attribute in your main module:
        # from your_package import __version__
        # return __version__

        # If 'Version' class from 'slpkg.views.version' is indeed used:
        ver = Version()
        return ver.version
    except NameError:
        logging.error(
            "The 'Version' class is not defined. Please ensure 'from slpkg.views.version import Version' is correct.")
        return "0.0.0"  # Return a default low version to allow updates if class is missing


def get_repo_latest_version(url: str) -> Union[Any, None]:  # pylint: disable=[R0911]
    """
    Fetches the latest version from the repository's ChangeLog file.

    Args:
        url (str): The URL to the ChangeLog.txt file.

    Returns:
        str | None: The latest version string if found, otherwise None.
    """
    try:
        # Make a GET request with a timeout to prevent indefinite waiting
        response = requests.get(url, timeout=10)
        # Raise an HTTPError for bad responses (4xx or 5xx status codes)
        response.raise_for_status()

        # Search for the first line that starts with the defined VERSION_PREFIX
        for line in response.text.splitlines():
            if line.startswith(VERSION_PREFIX):
                try:
                    # Assuming the format is '## vX.Y.Z' or similar.
                    # split() will create a list like ['##', 'vX.Y.Z', ...]
                    return line.split()[2].strip()
                except IndexError:
                    # Log a warning if the version format is unexpected on a matching line
                    logging.warning("Could not parse version from line: '%s'. Expected format like '## vX.Y.Z'.", line)
                    return None

        # If no line with the version prefix is found
        logging.warning("No version found with the specified prefix.")
        return None

    except requests.exceptions.Timeout:
        logging.error("The request timed out after 10 seconds while trying to reach the URL: %s", url)
        return None
    except requests.exceptions.ConnectionError:
        logging.error("Could not connect to the URL: %s. Check your internet connection or the URL.", url)
        return None
    except requests.exceptions.HTTPError as e:
        # Log specific HTTP errors (e.g., 404 Not Found, 403 Forbidden)
        logging.error("HTTP error occurred while accessing %s: %s - %s", url, e.response.status_code, e.response.reason)
        return None
    except requests.exceptions.RequestException as e:
        # Catch any other request-related exceptions not caught by more specific requests exceptions
        logging.error("An unexpected request error occurred while accessing %s: %s", url, e)
        return None


def check_self_update() -> None:
    """
    Checks for a newer version of the software and informs the user.
    """
    green: str = config_load.green
    cyan: str = config_load.cyan
    yellow: str = config_load.yellow
    endc: str = config_load.endc
    parsed_installed: Version_parse = parse_version('0.0.0')
    parsed_repo: Version_parse = parse_version('0.0.0')

    installed_version_str = get_installed_version()
    repo_version_str = get_repo_latest_version(CHANGELOG_URL)

    # If we couldn't determine the repository's latest version, we can't proceed
    if not repo_version_str:
        logging.info("Could not determine the latest version from the repository. Update check aborted.")
        return

    try:
        # Parse version strings into comparable version objects
        parsed_installed = parse_version(installed_version_str)
        parsed_repo = parse_version(repo_version_str)
    except InvalidVersion as e:
        # Catch general exceptions during version parsing (e.g., InvalidVersion)
        logging.error("Failed to parse versions '%s' or '%s': %s. Please ensure valid version strings.",
                      installed_version_str, repo_version_str, e)

    # Compare the parsed versions
    if parsed_repo > parsed_installed:
        print(f"Update available: Version {green}{parsed_repo}{endc} is newer than your current {yellow}{parsed_installed}{endc}.")
        print(f"Please visit the install page: '{cyan}https://dslackw.gitlab.io/slpkg/install{endc}'")
    else:
        print(f"Current version ({green}{parsed_installed}{endc}) is up to date. No new updates found.")
