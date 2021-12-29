from datetime import datetime
from typing import Iterable
from typing import Optional
from typing import Union

import pandas as pd
import requests

from blueskyapi import default_config
from blueskyapi import errors


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
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or default_config.api_key
        self.base_url = base_url or default_config.base_url

        self.session = requests.Session()

        if self.api_key is not None:
            self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})

    def latest_forecast(
        self,
        lat: float,
        lon: float,
        forecast_distances: Iterable[int] = None,
        columns: Iterable[str] = None,
    ) -> pd.DataFrame:
        response = self._get(
            "/forecasts/gfs_0p25/latest",
            params=dict(
                lat=lat,
                lon=lon,
                forecast_distances=_prepare_comma_separated_list(
                    forecast_distances, "forecast_distances"
                ),
                columns=_prepare_comma_separated_list(columns, "columns"),
            ),
        )
        return _create_dataframe(response)

    def forecast_history(
        self,
        lat: float,
        lon: float,
        min_forecast_moment: Union[datetime, str],
        max_forecast_moment: Optional[Union[datetime, str]] = None,
        forecast_distances: Optional[Iterable[int]] = None,
        columns: Optional[Iterable[str]] = None,
    ) -> pd.DataFrame:
        response = self._get(
            "/forecasts/gfs_0p25/history",
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
            ),
        )
        return _create_dataframe(response)

    def _get(self, endpoint: str, params: dict = {}) -> bytes:
        url = self._url(endpoint)
        response = self.session.get(url, params=params)
        if response.ok:
            return response.content
        else:
            raise errors.request_error_from_response(response)

    def _url(self, endpoint: str) -> str:
        return self.base_url + endpoint
