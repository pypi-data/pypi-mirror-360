"""Simple utility functions to save and read json files."""

import json


def save_json(
    data: dict | list,
    file_path: str,
):
    """
    Utility to save python dictionary or list to a json file.
    """
    with open(file_path, mode="w", encoding="utf-8") as f:
        json.dump(obj=data, fp=f, indent=4)


def save_jsonl(
    data: dict | list,
    file_path: str,
):
    """
    Utility to save python dictionary or list to a json lines file.
    """
    with open(file_path, mode="w", encoding="utf-8") as f:
        if isinstance(data, dict):
            data = [data]
        for item in data:
            json.dump(obj=item, fp=f)
            f.write("\n")


def load_json(
    file_path: str,
) -> dict:
    """
    Utility to load a python dictionary or list from a json file.
    """
    with open(file_path, mode="r", encoding="utf-8") as f:
        _json = json.load(fp=f)

    if isinstance(_json, list):
        # always return a dict
        return {"data": _json}

    return _json


def load_jsonl(
    file_path: str,
) -> list:
    """
    Utility to load a python dictionary or list from a json lines file.
    """
    with open(file_path, mode="r", encoding="utf-8") as f:
        _json = [json.loads(line) for line in f]

    return _json
