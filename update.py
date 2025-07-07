# update.py
# For sending requests to a networked digital signage device running mpv and
# simple-mpv-webui (https://github.com/open-dynaMIX/simple-mpv-webui).

import pathlib
import requests
import socket
import sys
from urllib import parse


# Set this to the IP of the signage device as a string if you set it manually.
# The default value assumes the device has the hostname "sign", and will
# attempt to resolve that name to an IP address.
IP = socket.gethostbyname("sign.local")

BASE_URL = f"http://{IP}:8080/api/"
HEADERS = {"Content-Type": "application/json"}


def get_collection(path: str):
    """Get the paths returned from simple-mpv-webui for a collection
    and return a list."""

    collection_path = parse.quote(path, safe="")

    try:
        collection_request = requests.get(BASE_URL + "collections/" + collection_path)
        collection_request.raise_for_status()
        collection_json = collection_request.json()
        output = []
        for i in collection_json:
            if not i["is-directory"]:
                output.append(i["path"])

    except Exception as e:
        print(f"Error getting collection {path}: {e}")
        exit(1)

    return output


def set_asset(path: str):
    """Post to simple-mpv-webui to change the current playlist to the
    path."""

    asset_path = parse.quote(path, safe="")
    try:
        set_request = requests.post(BASE_URL + "loadfile/" + asset_path)
        set_request.raise_for_status()

    except Exception as e:
        print(f"Error changing playlist to {path}: {e}")
        exit(1)


def main():
    idle_path = ""
    game_assets = []

    try:
        collections_request = requests.get(BASE_URL + "collections")
        collections_request.raise_for_status()
        collections_json = collections_request.json()
        collections: list[str] = []
        for i in collections_json:
            if i["is-directory"]:
                collections.append(i["path"])

        for collection in collections:
            if collection.endswith("games"):
                game_assets = get_collection(collection)
            elif collection.endswith("idle"):
                idle_path = collection

    except Exception as e:
        print(f"Error getting collections: {e}")
        exit(1)

    # Create a dict with the game names as keys and the paths as values.
    game_dict = {}
    for game in game_assets:
        game_dict[pathlib.Path(game).stem] = game

    # If a game name is given as the first command line argument, set the
    # display to that game. Otherwise, set to the idle collection as a
    # playlist.
    if len(sys.argv) > 1:
        if sys.argv[1] in game_dict:
            set_asset(game_dict[sys.argv[1]])
        else:
            print(f"Error: {sys.argv[1]} not in game asset collection.")
            exit(1)
    else:
        set_asset(idle_path)


if __name__ == "__main__":
    main()
