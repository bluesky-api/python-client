import json
from typing import Type

import requests


class Error(Exception):
    pass


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
    pass


class InvalidApiKey(RequestError):
    pass


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
