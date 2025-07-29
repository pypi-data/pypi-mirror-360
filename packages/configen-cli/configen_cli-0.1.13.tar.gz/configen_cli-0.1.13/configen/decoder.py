import gzip
import base64
import json


def compress_and_encode(data: dict) -> str:
    json_bytes = json.dumps(data).encode('utf-8')
    compressed = gzip.compress(json_bytes)
    return base64.b64encode(compressed).decode('utf-8')


def decode_and_decompress(data: str) -> dict:
    decoded = base64.b64decode(data)
    decompressed = gzip.decompress(decoded)
    return json.loads(decompressed.decode('utf-8'))
