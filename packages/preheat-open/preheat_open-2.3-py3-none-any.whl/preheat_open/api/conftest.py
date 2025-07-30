import pathlib
from typing import Generator

import pytest

import preheat_open.api as papi
import preheat_open.api.mocks as mocks


@pytest.fixture(scope="session", autouse=True)
def test_config() -> None:
    from preheat_open.api.configuration import ConfigLoader

    file_path = f"{str(pathlib.Path(__file__).parent.resolve())}/test/mocks/configurations/config.yaml"
    ConfigLoader(path=file_path, force_reload=True)


@pytest.fixture(scope="session")
def mock_adapter() -> Generator[mocks.MockApiAdapter, None, None]:
    with mocks.MockApiAdapter(
        mocks_path=f"{str(pathlib.Path(__file__).parent.resolve())}/test/mocks",
    ) as adapter:
        yield adapter


@pytest.fixture(scope="session")
def api_adapter() -> Generator[papi.ApiAdapter, None, None]:
    with papi.ApiAdapter() as adapter:
        yield adapter
