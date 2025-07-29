from . import generic

from .client import Client


@Client._register_endpoint
def find_users(nickname=None, uid=None, auth_token=None):
    if not bool(nickname) ^ bool(uid):
        raise ValueError("Specify exactly one of nickname, uid")
    params = {"p": "false"}
    if nickname:
        params.update({"s": nickname, "t": "nickname"})
    elif uid:
        params.udpate({"s": uid, "t": "uid"})
    return generic.process_response(
        generic.geotastic_api_request(
            "https://api.geotastic.net/v1/user/getUserSuggestions.php",
            "GET",
            auth_token,
            params=params,
        )
    )


@Client._register_endpoint
def get_public_user_info(uid, auth_token=None):
    return generic.process_response(
        generic.geotastic_api_request(
            "https://api.geotastic.net/v1/user/getPublicUserInfoByUid.php",
            "GET",
            auth_token,
            params={"uid": uid},
        )
    )


@Client._register_endpoint
def get_achievements(uid, auth_token=None):
    return generic.process_response(
        generic.geotastic_api_request(
            "https://api.geotastic.net/v1/user/getAchievementsByUser.php",
            "GET",
            auth_token,
            params={"uid": uid},
        )
    )


@Client._register_endpoint
def get_statistics(uid, auth_token=None):
    data = generic.encode_encdata({"userUid": uid})
    return generic.process_response(
        generic.geotastic_api_request(
            "https://api.geotastic.net/v1/user/getUserStatistics.php",
            "POST",
            auth_token,
            json={"enc": data},
        )
    )
