from datetime import datetime

import pandas as pd
import requests

from blueskyapi import default_config
from blueskyapi import errors


def _create_dataframe(response):
    df = pd.read_json(response)
    df.prediction_moment = pd.to_datetime(df.prediction_moment)
    return df


def _prepare_comma_separated_list(value, name):
    if value is None:
        return None
    elif isinstance(value, str):
        return value

    try:
        return ",".join(str(v) for v in value)
    except TypeError:
        raise TypeError(f"{name} should be an array of values or None, got {value}")


def _prepare_datetime(value, name):
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
    def __init__(self, api_key=None, base_url=None):
        self.api_key = api_key or default_config.api_key
        self.base_url = base_url or default_config.base_url

        self.session = requests.Session()

        if self.api_key is not None:
            self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})

    def latest_forecast(self, lat, lon, prediction_distances=None, columns=None):
        response = self._get(
            "/forecasts/gfs_0p25/latest",
            params=dict(
                lat=lat,
                lon=lon,
                prediction_distances=_prepare_comma_separated_list(
                    prediction_distances, "prediction_distances"
                ),
                columns=_prepare_comma_separated_list(columns, "columns"),
            ),
        )
        return _create_dataframe(response)

    def forecast_history(
        self,
        lat,
        lon,
        min_prediction_moment,
        max_prediction_moment=None,
        prediction_distances=None,
        columns=None,
    ):
        response = self._get(
            "/forecasts/gfs_0p25/history",
            params=dict(
                lat=lat,
                lon=lon,
                min_prediction_moment=_prepare_datetime(
                    min_prediction_moment, "min_prediction_moment"
                ),
                max_prediction_moment=_prepare_datetime(
                    max_prediction_moment, "max_prediction_moment"
                ),
                prediction_distances=_prepare_comma_separated_list(
                    prediction_distances, "prediction_distances"
                ),
                columns=_prepare_comma_separated_list(columns, "columns"),
            ),
        )
        return _create_dataframe(response)

    def _get(self, endpoint, params={}):
        url = self._url(endpoint)
        response = self.session.get(url, params=params)
        if response.ok:
            return response.content
        else:
            raise errors._request_error_from_response(response)

    def _url(self, endpoint):
        return self.base_url + endpoint
