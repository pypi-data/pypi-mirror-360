import orjson as json

from typing import Any


def default_json_dumps(obj) -> bytes:
    return json.dumps(
        obj,
        option=(
            json.OPT_SERIALIZE_NUMPY
            | json.OPT_SERIALIZE_UUID
        )
    )


def default_pretty_json_dumps(obj) -> bytes:
    return json.dumps(
        obj,
        option=(
            json.OPT_SERIALIZE_NUMPY
            | json.OPT_SERIALIZE_UUID
            | json.OPT_INDENT_2
        )
    )


class JSONSettings:
    def __init__(self):
        self._loads = json.loads
        self._dumps = default_json_dumps
        self._pretty_dumps = default_pretty_json_dumps

    def use(
        self,
        loads=json.loads,
        dumps=default_json_dumps,
        pretty_dumps=default_pretty_json_dumps,
    ):
        self._loads = loads
        self._dumps = dumps
        self._pretty_dumps = pretty_dumps

    def loads(self, text: str) -> Any:
        return self._loads(text)

    def dumps(self, obj: Any) -> bytes:
        return self._dumps(obj)

    def pretty_dumps(self, obj: Any) -> bytes:
        return self._pretty_dumps(obj)


json_settings = JSONSettings()