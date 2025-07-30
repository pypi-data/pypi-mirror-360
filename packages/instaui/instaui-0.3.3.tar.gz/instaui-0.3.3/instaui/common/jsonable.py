import orjson as json
import datetime
from enum import Enum


class Jsonable:
    def _to_json_dict(self):
        data = {k: v for k, v in self.__dict__.items() if k[:1] != "_"}

        return data


def json_default(obj):
    if isinstance(obj, float):
        return None
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, Jsonable):
        return obj._to_json_dict()


def dumps(obj, indent=False):
    def json_default_wrapper(obj):
        for fn in [json_default]:
            res = fn(obj)
            if res is not None:
                return res

    return json.dumps(
        obj, default=json_default_wrapper, option=json.OPT_INDENT_2 if indent else 0
    ).decode("utf-8")


def dumps2dict(obj):
    return json.loads(dumps(obj))
