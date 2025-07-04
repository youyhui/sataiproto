import hashlib
import string
import re


def generate_user_id(input_str, length=6):
    hash_obj = hashlib.sha256(input_str.encode())
    hex_digest = hash_obj.hexdigest()
    num = int(hex_digest, 16)
    base62_chars = string.ascii_letters + string.digits
    base62 = ""
    while num > 0 and len(base62) < length:
        base62 += base62_chars[num % 62]
        num //= 62
    return base62


def validEmail(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None