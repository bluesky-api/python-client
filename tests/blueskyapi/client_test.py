from blueskyapi import Client


def test_init_defaults():
    client = Client()
    assert client.base_url == "https://api.blueskyapi.io"
    assert client.api_key == None
