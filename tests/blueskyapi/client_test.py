from datetime import datetime

import numpy as np
import pandas as pd
import pytest
import responses

import blueskyapi


@pytest.fixture()
def client():
    return blueskyapi.Client()


default_result = [{"forecast_moment": "2021-12-27T18:00:00Z"}]


def add_api_response(path, *, result=default_result, status=200, api_key=None):
    matchers = []
    if api_key is not None:
        matchers.append(
            responses.matchers.header_matcher({"Authorization": f"Bearer {api_key}"})
        )

    responses.add(
        responses.GET,
        blueskyapi.default_config.base_url + path,
        json=result,
        status=status,
        match=matchers,
    )


def describe_init():
    def test_defaults(mocker):
        mocker.patch.multiple(
            "blueskyapi.default_config",
            base_url="the base url",
            api_key="the api key",
        )

        client = blueskyapi.Client()
        assert client.base_url == "the base url"
        assert client.api_key == "the api key"

    def test_with_args():
        client = blueskyapi.Client("api-key", base_url="https://example.com/api")
        assert client.base_url == "https://example.com/api"
        assert client.api_key == "api-key"


def describe_with_api_key():
    @responses.activate
    def when_valid():
        client = blueskyapi.Client(api_key="the-key")
        add_api_response(
            "/forecasts/gfs_0p25/latest?lat=53.5&lon=13.5", api_key="the-key"
        )
        client.latest_forecast(53.5, 13.5)

    @responses.activate
    def when_invalid():
        client = blueskyapi.Client(api_key="the-key")
        add_api_response(
            "/forecasts/gfs_0p25/latest?lat=53.5&lon=13.5",
            api_key="the-key",
            result={"detail": "Invalid API key"},
            status=401,
        )
        with pytest.raises(blueskyapi.errors.InvalidApiKey, match="401"):
            client.latest_forecast(53.5, 13.5)


def describe_latest_forecast():
    @responses.activate
    def test_defaults(client):
        add_api_response("/forecasts/gfs_0p25/latest?lat=53.5&lon=13.5")
        client.latest_forecast(53.5, 13.5)

    def describe_forecast_distances():
        @responses.activate
        def with_array(client):
            add_api_response(
                "/forecasts/gfs_0p25/latest?lat=53.5&lon=13.5&forecast_distances=0,24"
            )
            client.latest_forecast(53.5, 13.5, forecast_distances=[0, 24])

        @responses.activate
        def with_string(client):
            add_api_response(
                "/forecasts/gfs_0p25/latest?lat=53.5&lon=13.5&forecast_distances=0,24"
            )
            client.latest_forecast(53.5, 13.5, forecast_distances="0,24")

        @responses.activate
        def with_invalid_value(client):
            with pytest.raises(TypeError, match="forecast_distances should be"):
                client.latest_forecast(53.5, 13.5, forecast_distances=1.5)

    def describe_columns():
        @responses.activate
        def with_array(client):
            add_api_response(
                "/forecasts/gfs_0p25/latest?lat=53.5&lon=13.5&columns=col_a,col_b"
            )
            client.latest_forecast(53.5, 13.5, columns=["col_a", "col_b"])

        @responses.activate
        def with_string(client):
            add_api_response(
                "/forecasts/gfs_0p25/latest?lat=53.5&lon=13.5&columns=col_a,col_b"
            )
            client.latest_forecast(53.5, 13.5, columns="col_a,col_b")

        @responses.activate
        def with_invalid_value(client):
            with pytest.raises(TypeError, match="columns should be"):
                client.latest_forecast(53.5, 13.5, columns=1)

    @responses.activate
    def test_over_rate_limit(client):
        add_api_response(
            "/forecasts/gfs_0p25/latest?lat=53.5&lon=13.5",
            result={"the": "error"},
            status=429,
        )
        with pytest.raises(blueskyapi.errors.OverRateLimit, match="429"):
            client.latest_forecast(53.5, 13.5)

    @responses.activate
    def test_result(client):
        add_api_response(
            "/forecasts/gfs_0p25/latest?lat=53.5&lon=13.5",
            result=[{"forecast_moment": "2021-12-27T18:00:00Z", "some_column": 5}],
        )
        result = client.latest_forecast(53.5, 13.5)
        assert np.all(
            result.forecast_moment == [pd.to_datetime("2021-12-27T18:00:00Z")]
        )
        assert np.all(result.some_column == [5])

    @pytest.mark.vcr()
    def test_integration(client):
        result = client.latest_forecast(53.5, 13.5)

        assert len(result.columns) == 35
        assert len(result) == 15

        assert str(result.forecast_moment.dtype) == "datetime64[ns, UTC]"
        assert np.all(
            result.forecast_moment == pd.to_datetime("2021-12-29T00:00:00Z")
        )

        assert np.all(
            result.forecast_distance
            == [0, 3, 6, 9, 12, 15, 18, 21, 24, 48, 72, 96, 120, 144, 168]
        )

        print(result)
        assert np.all(result.apparent_temperature_at_2m > 250)
        assert np.all(result.apparent_temperature_at_2m < 290)


def describe_forecast_history():
    def describe_min_forecast_moments():
        @responses.activate
        def with_datetime(client):
            add_api_response(
                "/forecasts/gfs_0p25/history"
                "?lat=53.5&lon=13.5"
                "&min_forecast_moment=2021-12-27T18:00:00"
                "&max_forecast_moment=2021-12-28T00:00:00"
            )
            client.forecast_history(
                53.5,
                13.5,
                min_forecast_moment=datetime(2021, 12, 27, 18, 0),
                max_forecast_moment=datetime(2021, 12, 28, 0, 0),
            )

        @responses.activate
        def with_string(client):
            add_api_response(
                "/forecasts/gfs_0p25/history"
                "?lat=53.5&lon=13.5"
                "&min_forecast_moment=2021-12-27T18:00:00"
                "&max_forecast_moment=2021-12-28T00:00:00"
            )
            client.forecast_history(
                53.5,
                13.5,
                min_forecast_moment="2021-12-27T18:00:00",
                max_forecast_moment="2021-12-28T00:00:00",
            )

        @responses.activate
        def with_invalid_value(client):
            with pytest.raises(TypeError, match="min_forecast_moment should be"):
                client.forecast_history(53.5, 13.5, min_forecast_moment=1)

    def describe_max_forecast_moments():
        @responses.activate
        def with_none(client):
            add_api_response(
                "/forecasts/gfs_0p25/history"
                "?lat=53.5&lon=13.5"
                "&min_forecast_moment=2021-12-27T18:00:00"
            )
            client.forecast_history(
                53.5,
                13.5,
                min_forecast_moment=datetime(2021, 12, 27, 18, 0),
                max_forecast_moment=None,
            )
