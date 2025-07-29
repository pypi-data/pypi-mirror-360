from .errors import GeotasticAPIError
from .generic import decode_encdata
import requests
import os


def login(mail=None, password=None, token=None, fingerprint=None):
    if fingerprint is None:
        fingerprint = os.urandom(16).hex()
    creds = {}
    if mail:
        creds["mail"] = mail
    if password:
        creds["password"] = password
    if token:
        creds["token"] = token
    response = requests.post(
        "https://api.geotastic.net/v1/user/login.php",
        headers={
            "Origin": "https://geotastic.net",
            "Referer": "https://geotastic.net/",
        },
        json={"credentials": {"fingerprint": fingerprint, **creds}},
    )
    if response.ok:
        json_response = response.json()
        if json_response["status"] == "success":
            return decode_encdata(json_response["encData"])
        raise GeotasticAPIError(json_response["message"])
    raise GeotasticAPIError(f"{response.status} {response.reason}")
