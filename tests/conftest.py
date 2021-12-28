import os

import pytest


pytest_plugins = []


@pytest.fixture(scope="module")
def vcr_cassette_dir(request):
    return os.path.join("tests", "cassettes", request.module.__name__)
