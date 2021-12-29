import json
from typing import Type

import requests


class Error(Exception):
    """Base class for all blueskyapi errors."""


class RequestError(Error):
    def __init__(self, response: requests.Response):
        self.response = response

        msg = f"API responded with {response.status_code} - {response.reason}"
        if response.text:
            try:
                content = json.dumps(json.loads(response.text), indent=2)
            except json.decoder.JSONDecodeError:
                content = response.text
            msg += f"\n\n{content}"

        super().__init__(msg)


class OverRateLimit(RequestError):
    """Raised when a request exceeds the rate limit.

    The error message includes information about your current limits
    and used quotas.

    The limit can be increased by using an API key. Even the free plan
    includes a much higher limit than using the API without an API
    key. You can `create an API key here <https://blueskyapi.io/getting-started>`_.

    """


class InvalidApiKey(RequestError):
    """Raised when the given API key can't be found.

    Check `your API keys <https://blueskyapi.io/api-keys>`_ to make
    sure you're using a valid key.
    """


_errors_by_status_code = {
    requests.codes.too_many_requests: OverRateLimit,
    requests.codes.unauthorized: InvalidApiKey,
}


def _error_by_status_code(code: int) -> Type[RequestError]:
    if code in _errors_by_status_code:
        return _errors_by_status_code[code]
    else:
        return RequestError


def request_error_from_response(response: requests.Response) -> RequestError:
    klass = _error_by_status_code(response.status_code)
    return klass(response)
