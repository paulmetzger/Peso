import json


def read_config():
    with open('/home/paul/phd/papers/Realtime/scripts/configs/config.json') as c:
        return json.load(c)
