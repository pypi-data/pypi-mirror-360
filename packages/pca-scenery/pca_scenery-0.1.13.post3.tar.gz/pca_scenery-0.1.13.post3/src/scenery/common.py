"""General functions and classes used by other modules."""

import argparse
import collections
import enum
import os
import unittest
import requests
from typing import Any, Iterable, List, TypeVar, Union

from scenery import config

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import yaml



###################
# TYPES
###################

# NOTE mad: this is here to prevent circular import and still use those types
# either to check isinstance(x, cls) (see reponse_checker for instance),
# and type checking



class RemoteBackendTestCase(unittest.TestCase):
    """A TestCase for backend testing on a remote server."""
    mode: str
    session: requests.Session
    base_url: str
    headers: dict[str, str]

class RemoteFrontendTestCase(unittest.TestCase):
    """A TestCase for backend testing on a remote server."""
    mode: str
    driver: webdriver.Chrome
    # session: requests.Session
    base_url: str
    headers: dict[str, str]

class LoadTestCase(unittest.TestCase):
    """A TestCase for load testing on a remote server."""
    mode: str
    session: requests.Session
    headers: dict[str, str]
    base_url: str
    data: dict[str, List[dict[str, int|float]]]
    users:int
    requests_per_user:int


# NOTE mad: proper implementation is in django utils
class DjangoBackendTestCase:
    def __init__(self, *args, **kwargs):
            ImportError("django required")

class DjangoFrontendTestCase:
    def __init__(self, *args, **kwargs):
            ImportError("django required")


class Framework(enum.Enum):
    DJANGO = "django"


SceneryTestCaseTypes = Union[RemoteBackendTestCase, RemoteFrontendTestCase, LoadTestCase]

SceneryTestCase = TypeVar("SceneryTestCase", bound=SceneryTestCaseTypes)



###################
# SELENIUM
###################


def get_selenium_driver(headless: bool, page_load_timeout: int = 30) -> webdriver.Chrome:
    """Return a Selenium WebDriver instance configured for Chrome.

    Args:
        headless (bool): Whether to run Chrome in headless mode.
        page_load_timeout (int): Maximum time in seconds to wait for the page to load.
            If the timeout is exceeded, a TimeoutException will be thrown.

    Returns:
        webdriver.Chrome: Configured Chrome WebDriver instance.
    """
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    # NOTE mad: used to wait until domcontent loaded
    # see: https://www.selenium.dev/documentation/webdriver/drivers/options/
    chrome_options.page_load_strategy = 'eager' 
    if headless:
        chrome_options.add_argument("--headless=new")         # NOTE mad: For newer Chrome versions
        # chrome_options.add_argument("--headless")           
    driver = webdriver.Chrome(options=chrome_options)  #  service=service
    driver.implicitly_wait(10)
    driver.set_page_load_timeout(page_load_timeout)  # Set timeout for page load
    return driver



########
# YAML #
########


def read_yaml(filename: str) -> Any:
    """Read and parse a YAML file.

    Args:
        filename (str): The path to the YAML file to be read.

    Returns:
        Any: The parsed content of the YAML file.

    Raises:
        yaml.YAMLError: If there's an error parsing the YAML file.
        IOError: If there's an error reading the file.
    """
    with open(filename, "r") as f:
        return yaml.safe_load(f)


def iter_on_manifests(args: argparse.Namespace) -> Iterable[str]:
    for filename in os.listdir(config.manifests_folder):
        if args.manifest is not None and filename.replace(".yml", "") != args.manifest:
            continue

        yield filename



##################
# UNITTEST
##################


def serialize_unittest_result(result: unittest.TestResult) -> collections.Counter:
    """Serialize a unittest.TestResult object into a dictionary.

    Args:
        result (unittest.TestResult): The TestResult object to serialize.

    Returns:
        dict: A dictionary containing the serialized TestResult data.
    """
    d = {
        attr: getattr(result, attr)
        for attr in [
            "failures",
            "errors",
            "testsRun",
            "skipped",
            "expectedFailures",
            "unexpectedSuccesses",
        ]
    }
    d = {key: len(val) if isinstance(val, list) else val for key, val in d.items()}

    d["failed assertions"] = d["failures"]
    d["errors during execution"] = d["errors"]
    d["failed manifests"] = int(d["failures"] > 0)
    d["successful manifests"] = int(d["testsRun"])
    # d[""] = int(d["errors"] > 0)
    d.pop("errors")
    d.pop("failures")
    d.pop("testsRun")
    return collections.Counter(d)




