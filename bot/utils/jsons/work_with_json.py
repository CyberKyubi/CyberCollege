import os

import orjson as json


def create_path(file: str) -> str:
    return os.path.join(os.path.dirname(__file__), file)


def read_json(file: str) -> list:
    path = create_path(file)
    with open(path, 'rb') as json_file:
        json_data = json.loads(json_file.read())
        data = json_data['ids']
    return data


def write_json(file: str, value: list):
    path = create_path(file)
    with open(path, 'wb') as json_file:
        data = dict(ids=value)
        json_file.write(json.dumps(data))