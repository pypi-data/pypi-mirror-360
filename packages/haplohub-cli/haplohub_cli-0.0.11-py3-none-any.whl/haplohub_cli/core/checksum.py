from base64 import b64encode
from hashlib import md5


def calculate_checksum(file_path: str) -> str:
    return b64encode(md5(open(file_path, "rb").read()).digest()).decode("utf-8")
