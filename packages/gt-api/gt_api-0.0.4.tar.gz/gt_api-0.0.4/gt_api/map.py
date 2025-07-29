from . import generic
from .client import Client


@Client._register_endpoint
def create_tag(tag_name, auth_token=None):
    data = generic.encode_encdata({"tag": tag_name})
    return generic.process_response(
        generic.geotastic_api_request(
            "https://api.geotastic.net/v1/maps/createTagV2.php",
            "POST",
            auth_token,
            json={"enc": data},
        )
    )


@Client._register_endpoint
def get_public_drop_groups(map_id, include_tags=True, auth_token=None):
    return generic.process_response(
        generic.geotastic_api_request(
            "https://api.geotastic.net/v1/maps/getPublicDropGroups.php",
            "GET",
            params={"mapId": map_id, "withTags": include_tags},
        )
    )


@Client._register_endpoint
def create_drop_group(
    map_id, lat, lng, code, title, active=True, bias=1, auth_token=None, **properties
):
    data = {
        "mapId": map_id,
        "lat": lat,
        "lng": lng,
        "code": code,
        "title": title,
        "active": active,
        "bias": bias,
        "type": "group",
        **properties,
    }
    response = generic.geotastic_api_request(
        "https://api.geotastic.net/v1/maps/updateDropGroup.php",
        "POST",
        auth_token,
        json=data,
    )
    return generic.process_response(response)


@Client._register_endpoint
def update_drop_group(group_id, auth_token=None, **properties):
    data = {"id": group_id, **properties}
    response = generic.geotastic_api_request(
        "https://api.geotastic.net/v1/maps/updateDropGroup.php",
        "POST",
        auth_token,
        json=data,
    )
    return generic.process_response(response)


@Client._register_endpoint
def get_drop_groups(map_id, auth_token=None):
    response = generic.geotastic_api_request(
        "https://api.geotastic.net/v1/maps/getDropGroups.php",
        "GET",
        auth_token,
        params={"mapId": map_id},
    )
    return generic.process_response(response)


@Client._register_endpoint
def delete_drop_group(drop_group_id, auth_token=None):
    return generic.process_response(
        generic.geotastic_api_request(
            "https://api.geotastic.net/v1/maps/deleteDropGroupV2.php",
            "POST",
            auth_token,
            json={"dropGroupId": drop_group_id},
        )
    )


@Client._register_endpoint
def delete_drop(drop_id, auth_token=None):
    return generic.process_response(
        generic.geotastic_api_request(
            "https://api.geotastic.net/v1/maps/deleteDropV2.php",
            "POST",
            auth_token,
            json={"dropId": drop_id},
        )
    )


@Client._register_endpoint
def import_drops(drops, target_id, target_type, import_type="merge", auth_token=None):
    return generic.process_response(
        generic.geotastic_api_request(
            "https://api.geotastic.net/v1/drops/importDrops.php",
            "POST",
            auth_token,
            json={
                "drops": drops,
                "params": {
                    "targetId": target_id,
                    "targetType": target_type,
                    "importType": import_type,
                },
            },
        )
    )


@Client._register_endpoint
def get_map_drops(map_id, auth_token=None):
    return generic.process_response(
        generic.geotastic_api_request(
            "https://api.geotastic.net/v1/maps/getDrops.php",
            "GET",
            auth_token,
            params={"mapId": map_id},
        )
    )


@Client._register_endpoint
def get_group_drops(group_id, auth_token=None):
    return generic.process_response(
        generic.geotastic_api_request(
            "https://api.geotastic.net/v1/maps/getDrops.php",
            "GET",
            auth_token,
            params={"groupId": group_id},
        )
    )


@Client._register_endpoint
def update_map(map_id, auth_token=None, **properties):
    data = {"id": map_id, **properties}
    return generic.process_response(
        generic.geotastic_api_request(
            "https://api.geotastic.net/v1/maps/updateMapV2.php",
            "POST",
            auth_token,
            json={"enc": generic.encode_encdata(data)},
        )
    )


@Client._register_endpoint
def delete_map(map_id, auth_token=None):
    return generic.process_response(
        generic.geotastic_api_request(
            "https://api.geotastic.net/v1/maps/deleteMap.php",
            "POST",
            auth_token,
            data=str(map_id),
        )
    )


@Client._register_endpoint
def get_own_maps(auth_token=None):
    return generic.process_response(
        generic.geotastic_api_request(
            "https://api.geotastic.net/v1/maps/getMaps.php", "GET", auth_token
        )
    )


@Client._register_endpoint
def get_playable_maps(auth_token=None):
    return generic.process_response(
        generic.geotastic_api_request(
            "https://api.geotastic.net/v1/maps/getPlayableMaps.php", "GET", auth_token
        )
    )


@Client._register_endpoint
def random_single_map_drop(map_id, used_ids=[], auth_token=None):
    return generic.process_response(
        generic.geotastic_api_request(
            "https://api.geotastic.net/v1/maps/getRandomDropFromSingleDropMap.php",
            "GET",
            auth_token,
            params={"mapId": map_id, "usedIds": ",".join(map(str, used_ids))},
        )
    )


@Client._register_endpoint
def random_grouped_map_drop(
    map_id, removed_groups=[], used_ids=[], picker="balanced", auth_token=None
):
    response = geotastic_api_request(
        "https://api.geotastic.net/v1/maps/getRandomDropFromGroupedDropMap.php",
        "GET",
        auth_token,
        params={
            "mapId": map_id,
            "rg": ",".join(map(str, removed_groups)),
            "used": ",".join(map(str, used_ids)),
            "sm": picker,
        },
    )
    return process_response(response)


@Client._register_endpoint
def get_map_tags(map_id, auth_token=None):
    return generic.process_response(
        generic.geotastic_api_request(
            "https://api.geotastic.net/v1/maps/getTagsByMap.php",
            "GET",
            auth_token,
            params={"mapId": map_id},
        )
    )


@Client._register_endpoint
def get_maps_by_user(uid, auth_token=None):
    return generic.process_response(
        generic.geotastic_api_request(
            "https://api.geotastic.net/v1/maps/getPlayableMapsByUser.php",
            "GET",
            auth_token,
            params={"uid": uid},
        )
    )


@Client._register_endpoint
def get_map_info(map_id, auth_token=None):
    return generic.process_response(
        generic.geotastic_api_request(
            "https://api.geotastic.net/v1/maps/getPlayableMap.php",
            "GET",
            auth_token,
            params={"id": map_id},
        )
    )


@Client._register_endpoint
def increase_play_count(map_id, auth_token=None):
    response = generic.geotastic_api_request(
        "https://backend01.geotastic.net/v1/maps/incrementPlayedMapAmountV2.php",
        "POST",
        auth_token,
        json={"enc": generic.encode_encdata({"mapId": map_id})},
    )
    return generic.process_response(response)
