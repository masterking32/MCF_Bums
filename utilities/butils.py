def can_use(target_timestamp: int):
        import time
        if target_timestamp <= 0:
            return True
        
        current_timestamp = int(time.time())

        if current_timestamp >= target_timestamp:
            return False
        return True

def generate_boundary():
    import random

    characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    random_string = "".join(random.choices(characters, k=16))
    boundary = "----WebKitFormBoundary" + random_string
    return boundary


def generate_payload(boundary, data, utf8=False):
    if boundary is None or boundary == "":
        raise TypeError("Unable to generate payload, boundary required.")
    if not isinstance(data, dict):
        raise TypeError("Unable to generate payload, dict object required.")

    body = []
    for name, value in data.items():
        body.append(f"--{boundary}\r\n")
        body.append(f'Content-Disposition: form-data; name="{name}"\r\n\r\n')
        body.append(f"{value}\r\n")

    body.append(f"--{boundary}--\r\n")

    if utf8:
        return "".join(body).encode("utf-8")

    return "".join(body)


def generate_md5(message: str, output_length=32):
    import hashlib

    md5 = hashlib.md5()

    md5.update(message.encode("utf-8"))

    digest = md5.digest()

    if output_length == 32:
        return digest.hex()
    elif output_length == 16:
        return digest[:8].hex() + digest[8:].hex()
    else:
        raise ValueError("Output length must be 16 or 32.")


def round_int(num):
    num = int(num)
    if num < 1000:
        return str(num)
    elif num < 1000000:
        return str(round(num / 1000, 2)) + "k"
    elif num < 1000000000:
        return str(round(num / 1000000, 2)) + "m"
    elif num < 1000000000000:
        return str(round(num / 1000000000, 2)) + "b"
    else:
        return str(round(num / 1000000000000, 2)) + "t"


def normalize_name(string: str):
    import re

    if string.islower():
        return string.capitalize()

    words = re.findall(r"[a-z]+|[A-Z][a-z]*", string)

    if words:
        return " ".join([word.capitalize() for word in words])
    else:
        return string.capitalize()
