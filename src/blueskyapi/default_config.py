"""
Client instances created without an explicit API key will use the one specified in ``blueskyapi.default_config.api_key``::

    import blueskyapi

    blueskyapi.default_config.api_key = "your-api-key"

    client = blueskyapi.Client()
    client.api_key # => "your-api-key"
"""

base_url = "https://api.blueskyapi.io"

api_key = None
