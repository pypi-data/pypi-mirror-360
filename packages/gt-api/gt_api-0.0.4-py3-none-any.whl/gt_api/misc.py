from . import generic
from .client import Client


@Client._register_endpoint
def get_app_config(auth_token=None):
    return generic.process_response(
        generic.geotastic_api_request(
            "https://api.geotastic.net/v1/config/getAppConfig.php", "GET", auth_token
        )
    )


@Client._register_endpoint
def get_community_map_markers(auth_token=None):
    return generic.process_response(
        generic.geotastic_api_request(
            "https://api.geotastic.net/v1/communityMap/getMarkers.php",
            "GET",
            auth_token,
        )
    )


@Client._register_endpoint
def request_api_key(auth_token=None):
    data = generic.encode_encdata({})
    return generic.process_response(
        generic.geotastic_api_request(
            "https://api.geotastic.net/v1/config/requestApiKey.php",
            "POST",
            auth_token,
            json={"enc": data},
        )
    )
