import sys
from datetime import datetime
from typing import Iterable
from typing import Optional
from typing import Union

import pandas as pd
import requests

from blueskyapi import default_config
from blueskyapi import errors
from blueskyapi.__version__ import __version__


def _create_dataframe(response: bytes) -> pd.DataFrame:
    df = pd.read_json(response)
    df.forecast_moment = pd.to_datetime(df.forecast_moment)
    return df


def _prepare_comma_separated_list(
    value: Union[str, Iterable, None], name: str
) -> Optional[str]:
    if value is None:
        return None
    elif isinstance(value, str):
        return value

    try:
        return ",".join(str(v) for v in value)
    except TypeError:
        raise TypeError(f"{name} should be an array of values or None, got {value}")


def _prepare_datetime(value: Union[datetime, str, None], name: str) -> Optional[str]:
    if value is None:
        return None
    elif isinstance(value, datetime):
        return value.isoformat()
    elif isinstance(value, str):
        return value
    else:
        raise TypeError(
            f"{name} should be a datetime or ISO datetime string, got {value}"
        )


class Client:
    """Client to interact with the blueskyapi.io API.

    Data is returned as a ``pandas.DataFrame`` and includes the
    columns ``forecast_moment`` (UTC datetimes) and
    ``forecast_distances`` (integers), as well as any columns you
    select using the ``columns`` parameter.

    :param api_key: Your API key (create one `here <https://blueskyapi.io/api-keys>`_).
    :param base_url: Only for testing purposes. Don't use this parameter.
    """

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or default_config.api_key
        self.base_url = base_url or default_config.base_url

        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self._user_agent()})

        if self.api_key is not None:
            self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})

    def latest_forecast(
        self,
        lat: float,
        lon: float,
        forecast_distances: Iterable[int] = None,
        columns: Iterable[str] = None,
        dataset: Optional[str] = None,
    ) -> pd.DataFrame:
        """Obtain the latest forecast.

        :param lat: Latitude for which to fetch the forecast.
        :param lon: Longitude for which to fetch the forecast.
        :param forecast_distances: Forecast distances to fetch data for (hours from ``forecast_moment``).
        :param columns: Which variables to fetch (see `this page for available variables <https://blueskyapi.io/docs/data>`_).
        :param dataset: Which dataset to fetch data from (only for users on the Professional plan).
        """
        response = self._get(
            "/forecasts/latest",
            params=dict(
                lat=lat,
                lon=lon,
                forecast_distances=_prepare_comma_separated_list(
                    forecast_distances, "forecast_distances"
                ),
                columns=_prepare_comma_separated_list(columns, "columns"),
                dataset=dataset,
            ),
        )
        return _create_dataframe(response)

    def forecast_history(
        self,
        lat: float,
        lon: float,
        min_forecast_moment: Optional[Union[datetime, str]] = None,
        max_forecast_moment: Optional[Union[datetime, str]] = None,
        forecast_distances: Optional[Iterable[int]] = None,
        columns: Optional[Iterable[str]] = None,
        dataset: Optional[str] = None,
    ) -> pd.DataFrame:
        """Obtain historical forecasts.

        :param lat: Latitude for which to fetch the forecasts.
        :param lon: Longitude for which to fetch the forecasts.
        :param min_forecast_moment: The first forecast moment to include.
        :param max_forecast_moment: The last forecast moment to include.
        :param forecast_distances: Forecast distances to return data for (hours from ``forecast_moment``).
        :param columns: Which variables to fetch (see `this page for available variables <https://blueskyapi.io/docs/data>`_).
        :param dataset: Which dataset to fetch data from (only for users on the Professional plan).
        """
        response = self._get(
            "/forecasts/history",
            params=dict(
                lat=lat,
                lon=lon,
                min_forecast_moment=_prepare_datetime(
                    min_forecast_moment, "min_forecast_moment"
                ),
                max_forecast_moment=_prepare_datetime(
                    max_forecast_moment, "max_forecast_moment"
                ),
                forecast_distances=_prepare_comma_separated_list(
                    forecast_distances, "forecast_distances"
                ),
                columns=_prepare_comma_separated_list(columns, "columns"),
                dataset=dataset,
            ),
        )
        return _create_dataframe(response)

    def _get(self, endpoint: str, params: dict = {}) -> bytes:
        url = self._url(endpoint)
        response = self.session.get(url, params=params)
        if response.ok:
            return response.text
        else:
            raise errors.request_error_from_response(response)

    def _url(self, endpoint: str) -> str:
        return self.base_url + endpoint

    def _user_agent(self) -> str:
        python_version = sys.version.split(" ")[0]
        return " ".join(
            [
                f"blueskyapi-python/{__version__}",
                f"python/{python_version}",
                f"pandas/{pd.__version__}",
                f"requests/{requests.__version__}",
            ]
        )
