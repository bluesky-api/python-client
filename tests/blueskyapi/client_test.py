from datetime import datetime

import numpy as np
import pandas as pd
import pytest
import responses

import blueskyapi


class TestInit:
    def test_defaults(self, mocker):
        mocker.patch.multiple(
            "blueskyapi.default_config",
            base_url="the base url",
            api_key="the api key",
        )

        client = blueskyapi.Client()
        assert client.base_url == "the base url"
        assert client.api_key == "the api key"

    def test_with_args(self):
        client = blueskyapi.Client("api-key", base_url="https://example.com/api")
        assert client.base_url == "https://example.com/api"
        assert client.api_key == "api-key"


@pytest.fixture()
def client():
    return blueskyapi.Client()


default_result = [{"prediction_moment": "2021-12-27T18:00:00Z"}]


def add_api_response(path, *, result=default_result, status=200):
    responses.add(
        responses.GET,
        blueskyapi.default_config.base_url + path,
        json=result,
        status=status,
    )


class TestLatestForecast:
    @responses.activate
    def test_defaults(self, client):
        add_api_response("/forecasts/gfs_0p25/latest?lat=53.5&lon=13.5")
        client.latest_forecast(53.5, 13.5)

    @responses.activate
    def test_with_distances_as_array(self, client):
        add_api_response(
            "/forecasts/gfs_0p25/latest?lat=53.5&lon=13.5&prediction_distances=0,24"
        )
        client.latest_forecast(53.5, 13.5, prediction_distances=[0, 24])

    @responses.activate
    def test_with_distances_as_string(self, client):
        add_api_response(
            "/forecasts/gfs_0p25/latest?lat=53.5&lon=13.5&prediction_distances=0,24"
        )
        client.latest_forecast(53.5, 13.5, prediction_distances="0,24")

    @responses.activate
    def test_with_invalid_distances(self, client):
        with pytest.raises(TypeError, match="prediction_distances should be"):
            client.latest_forecast(53.5, 13.5, prediction_distances=1.5)

    @responses.activate
    def test_with_columns_as_array(self, client):
        add_api_response(
            "/forecasts/gfs_0p25/latest?lat=53.5&lon=13.5&columns=col_a,col_b"
        )
        client.latest_forecast(53.5, 13.5, columns=["col_a", "col_b"])

    @responses.activate
    def test_with_columns_as_string(self, client):
        add_api_response(
            "/forecasts/gfs_0p25/latest?lat=53.5&lon=13.5&columns=col_a,col_b"
        )
        client.latest_forecast(53.5, 13.5, columns="col_a,col_b")

    @responses.activate
    def test_with_invalid_columns(self, client):
        with pytest.raises(TypeError, match="columns should be"):
            client.latest_forecast(53.5, 13.5, columns=1)

    @responses.activate
    def test_with_selection(self, client):
        add_api_response(
            "/forecasts/gfs_0p25/latest"
            "?lat=53.5&lon=13.5"
            "&prediction_distances=0,24"
            "&columns=apparent_temperature_at_2m"
        )
        client.latest_forecast(
            53.5,
            13.5,
            prediction_distances=[0, 24],
            columns=["apparent_temperature_at_2m"],
        )

    @responses.activate
    def test_over_rate_limit(self, client):
        add_api_response(
            "/forecasts/gfs_0p25/latest?lat=53.5&lon=13.5",
            result={"the": "result"},
            status=429,
        )
        with pytest.raises(blueskyapi.errors.OverRateLimit, match="429"):
            client.latest_forecast(53.5, 13.5)

    @responses.activate
    def test_result(self, client):
        add_api_response(
            "/forecasts/gfs_0p25/latest?lat=53.5&lon=13.5",
            result=[{"prediction_moment": "2021-12-27T18:00:00Z", "some_column": 5}],
        )
        result = client.latest_forecast(53.5, 13.5)
        assert np.all(
            result.prediction_moment == [pd.to_datetime("2021-12-27T18:00:00Z")]
        )
        assert np.all(result.some_column == [5])

    @pytest.mark.vcr()
    def test_integration(self, client):
        result = client.latest_forecast(53.5, 13.5)

        assert len(result.columns) == 35
        assert len(result) == 15

        assert str(result.prediction_moment.dtype) == "datetime64[ns, UTC]"
        assert np.all(
            result.prediction_moment == pd.to_datetime("2021-12-27T06:00:00Z")
        )

        assert np.all(
            result.forecast_distance
            == [0, 3, 6, 9, 12, 15, 18, 21, 24, 48, 72, 96, 120, 144, 168]
        )

        assert np.all(result.apparent_temperature_at_2m > 250)
        assert np.all(result.apparent_temperature_at_2m < 290)
