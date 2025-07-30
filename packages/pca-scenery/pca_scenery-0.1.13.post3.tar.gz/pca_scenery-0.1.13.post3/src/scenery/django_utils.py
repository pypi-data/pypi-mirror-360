from typing import IO, Any

from django.test.runner import DiscoverRunner as DjangoDiscoverRunner
import django.test
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium import webdriver

class DjangoBackendTestCase(django.test.TestCase):
    """A Django TestCase for backend testing."""

class DjangoFrontendTestCase(StaticLiveServerTestCase):
    """A Django TestCase for frontend testing."""
    base_url: str
    driver: webdriver.Chrome


def overwrite_get_runner_kwargs(
    django_runner: DjangoDiscoverRunner, stream: IO
) -> dict[str, Any]:
    """Overwrite the get_runner_kwargs method of Django's DiscoverRunner.

    This function is used to avoid printing Django test output by redirecting the stream.

    Args:
        django_runner (DiscoverRunner): The Django test runner instance.
        stream: The stream to redirect output to.

    Returns:
        dict: A dictionary of keyword arguments for the test runner.

    Notes:
        see django.test.runner.DiscoverRunner.get_runner_kwargs
    """
    kwargs = {
        "failfast": django_runner.failfast,
        "resultclass": django_runner.get_resultclass(),
        "verbosity": django_runner.verbosity,
        "buffer": django_runner.buffer,
        # NOTE: this is the line below that changes compared to the original
        "stream": stream,
    }
    return kwargs


class CustomDiscoverRunner(DjangoDiscoverRunner):
    """Custom test runner that allows for stream capture."""
    
    # NOTE mad: this was done to potentially shut down the original stream
    # NOTE mad: used both in rehearsal and core module (for the runner
    # TODO mad: once we fit FastAPI, this runner should only be used 
    # for the django backend and frontend test

    def __init__(self, stream: Any , *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.stream = stream

    # def __del__(self):
    #     print(self.stream.getvalue())


    def get_test_runner_kwargs(self) -> dict[str, Any]:
        """Overwrite the original from django.test.runner.DiscoverRunner."""
        return overwrite_get_runner_kwargs(self, self.stream)


