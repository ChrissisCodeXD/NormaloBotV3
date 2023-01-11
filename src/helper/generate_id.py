import hashlib
import time


def generate_id() -> str:
    return str(hashlib.md5(f"{time.time()}".encode()).hexdigest())
