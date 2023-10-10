from httpx._multipart import DataField
from httpx._multipart import FileField
from httpx._multipart import MultipartStream


def verify_stream_contains(key: str, value: str, stream: MultipartStream):
    for item in stream.fields:
        if isinstance(item, FileField):
            continue
        elif isinstance(item, DataField) and item.name == key:
            assert item.value == value, f"Key {item.value} /= {value}"
            return

    msg = f'Key "{key}" with value "{value}" not found in stream'
    raise AssertionError(msg)
