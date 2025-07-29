import json
from json import JSONEncoder
from typing import Any

from cyberfusion.SystemdSupport import Unit

from cyberfusion.QueueSupport.sentinels import UNKNOWN


class CustomEncoder(JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, Unit):
            return {"name": o.name}
        elif o == UNKNOWN:
            return "unknown"

        return super().default(o)


def json_serialize(obj: Any) -> str:
    return json.dumps(obj, cls=CustomEncoder)
