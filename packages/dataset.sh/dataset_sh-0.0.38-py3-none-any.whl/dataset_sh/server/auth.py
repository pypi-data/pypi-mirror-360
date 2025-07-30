import json
import secrets

from werkzeug.security import generate_password_hash, check_password_hash


def generate_password():
    return secrets.token_hex(16)


def encode_key(username, password):
    kid = secrets.token_hex(4)
    key = json.dumps({
        'key_id': kid,
        'username': username,
        'password': password
    })
    return f"dsh-key:{username}:{kid}:{password}"


def decode_key(key_str):
    parts = key_str.split(':')
    if len(parts) != 4:
        return None
    [header, username, key_name, key] = parts
    if header != 'dsh-key':
        return None
    return username, key


def verify_password(password, hashed_password):
    return check_password_hash(hashed_password, password)


def hash_password(password):
    return generate_password_hash(password)
