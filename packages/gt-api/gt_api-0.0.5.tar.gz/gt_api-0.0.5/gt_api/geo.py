from . import generic
from .client import Client


# reverse geocoding
@Client._register_endpoint
def reverse(lat, lng, auth_token=None, omit_border_data=True, skip_state_check=False):
    enc = generic.encode_encdata(
        {
            "latLng": {"lat": lat, "lng": lng},
            "omitBorderData": omit_border_data,
            "skipStateCheck": skip_state_check,
        }
    )
    response = generic.process_response(
        generic.geotastic_api_request(
            "https://api01.geotastic.net/reverseV4", "POST", json={"enc": enc}
        )
    )
    return response
