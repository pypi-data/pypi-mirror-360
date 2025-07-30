import base64
import functools
import json

json_dumps = functools.partial(json.dumps, ensure_ascii=False)


class BytesEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return base64.b64encode(obj).decode('utf-8')
        return super().default(obj)


def base64_to_bytes(base64_str, encoding="utf-8") -> bytes:
    return base64.b64decode(base64_str.encode(encoding))
