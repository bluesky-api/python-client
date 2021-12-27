import json

from requests import codes


class Error(Exception):
    pass


class RequestError(Error):
    def __init__(self, response=None):
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


_errors_by_status_code = {
    codes.too_many_requests: OverRateLimit,
}


def _error_by_status_code(code):
    if code in _errors_by_status_code:
        return _errors_by_status_code[code]
    else:
        return RequestError


def _request_error_from_response(response):
    klass = _error_by_status_code(response.status_code)
    return klass(response)
