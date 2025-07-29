import json, requests

def _fetch_master_data() -> dict:
    try:
        response = requests.get("https://master1.ddnet.org/ddnet/15/servers.json", timeout=30)
        response.raise_for_status()
        return json.loads(response.text)
    except requests.exceptions.RequestException as e:
        raise e

def _fetch_player_data(name) -> dict:
    try:
        response = requests.get("https://ddstats.tw/player/json", params={"player": name}, timeout=30)
        response.raise_for_status()
        return json.loads(response.text)
    except requests.exceptions.RequestException as e:
        raise e

def _fetch_map_data(_map) -> dict:
    try:
        response = requests.get("https://ddstats.tw/map/json", params={"map": _map}, timeout=30)
        response.raise_for_status()
        return json.loads(response.text)
    except Exception as e:
        raise e

def _fetch_profile_data(name) -> dict:
    try:
        response = requests.get("https://ddstats.tw/profile/json", params={"player": name}, timeout=30)
        response.raise_for_status()
        return json.loads(response.text)
    except requests.exceptions.RequestException as e:
        raise e
