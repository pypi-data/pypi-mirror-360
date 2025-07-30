import json
def dump_if_json(obj):
    return json.dumps(obj) if isinstance(obj, dict) else obj
