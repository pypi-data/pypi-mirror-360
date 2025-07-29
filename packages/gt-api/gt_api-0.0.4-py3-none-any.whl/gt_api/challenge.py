from . import generic
from .client import Client


@Client._register_endpoint
def get_all_user_challenges(auth_token=None):
    return generic.process_response(
        generic.geotastic_api_request(
            "https://api.geotastic.net/v1/challenge/getAllUserChallenges.php",
            "GET",
            auth_token,
        )
    )


@Client._register_endpoint
def get_challenge_drops(challenge_id, auth_token=None):
    return generic.process_response(
        generic.geotastic_api_request(
            "https://api.geotastic.net/v1/challenge/getChallengeDrops.php",
            "GET",
            auth_token,
            params={"id": challenge_id},
        )
    )


@Client._register_endpoint
def get_challenge_results(challenge_id, auth_token=None):
    return generic.process_response(
        generic.geotastic_api_request(
            "https://api.geotastic.net/v1/challenge/getChallengeResults.php",
            "GET",
            auth_token,
            params={"id": challenge_id},
        )
    )


@Client._register_endpoint
def get_own_challenges(auth_token=None):
    return generic.process_response(
        generic.geotastic_api_request(
            "https://api.geotastic.net/v1/challenge/getOwnChallenges.php",
            "GET",
            auth_token,
        )
    )
