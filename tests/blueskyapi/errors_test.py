import inspect
import json

import requests
from doubles import InstanceDouble
from doubles import allow

from blueskyapi import errors


def describe_request_error():
    def with_json_response():
        response = InstanceDouble(
            "requests.Response",
            status_code=400,
            reason="Some reason",
            text=json.dumps({"some": "json"}),
        )
        error = errors.RequestError(response)

        str(error) == inspect.cleandoc(
            """
            API responded with 400 - Some reason

            {
              "some": "json"
            }
            """
        )

    def with_text_response():
        response = InstanceDouble(
            "requests.Response",
            status_code=400,
            reason="Some reason",
            text="Non-json text",
        )
        error = errors.RequestError(response)

        str(error) == inspect.cleandoc(
            """
            API responded with 400 - Some reason

            Non-json text
            """
        )


def test_error_by_status_code():
    assert (
        errors._error_by_status_code(requests.codes.too_many_requests)
        == errors.OverRateLimit
    )
    assert (
        errors._error_by_status_code(requests.codes.unauthorized)
        == errors.InvalidApiKey
    )
    assert errors._error_by_status_code(1234) == errors.RequestError


def test_request_error_from_response():
    response = InstanceDouble(
        "requests.Response",
        status_code=requests.codes.too_many_requests,
        reason="Too many requests",
        text=json.dumps({"some": "json"}),
    )
    error = errors.request_error_from_response(response)
    assert type(error) == errors.OverRateLimit
    assert error.response == response
