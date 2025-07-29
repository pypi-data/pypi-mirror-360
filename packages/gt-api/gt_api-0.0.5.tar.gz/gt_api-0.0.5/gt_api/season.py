from . import generic
from .client import Client


@Client._register_endpoint
def get_season(auth_token=None):
    return generic.process_response(
        generic.geotastic_api_request(
            "https://api.geotastic.net/v1/season/getSeason.php", "GET", auth_token
        )
    )
