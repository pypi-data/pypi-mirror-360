import datetime
from urllib.parse import urlencode

import jwt
from flask import request


def get_token(
        secret_key,
        action,
        filename,
        expiration_minutes=5
):
    # Add expiration time (exp) and issued at (iat) claims

    payload = {
        'action': action,
        'filename': filename
    }

    now = datetime.datetime.now(datetime.UTC)
    payload.update({
        'exp': now + datetime.timedelta(minutes=expiration_minutes),
        'iat': now
    })

    # Create the JWT token
    token = jwt.encode(
        payload=payload,
        key=secret_key,
        algorithm='HS256'
    )

    return token


def extract_token(token, secret_key):
    try:
        # Verify and decode the token
        payload = jwt.decode(
            jwt=token,
            key=secret_key,
            algorithms=['HS256']
        )
        return payload

    except jwt.ExpiredSignatureError:
        # Token has expired
        return None
    except jwt.InvalidTokenError:
        # Token is invalid
        return None


def extract_token_from_request(secret_key):
    token = request.args.get('token')
    return extract_token(token, secret_key)


def create_download_token(secret_key, filename):
    return get_token(secret_key, 'download', filename, expiration_minutes=10)


def verify_download_token(secret_key, filename):
    token = request.args.get('token')
    payload = extract_token(token, secret_key)
    if payload is None:
        return False
    if payload['action'] != 'download':
        return False
    if payload['filename'] != filename:
        return False
    return True


def create_upload_token(secret_key, filename):
    return get_token(secret_key, 'upload', filename, expiration_minutes=3600)


def verify_upload_token(secret_key, filename):
    token = request.args.get('token')
    payload = extract_token(token, secret_key)
    if payload is None:
        return False
    if payload['action'] != 'upload':
        return False
    if payload['filename'] != filename:
        return False
    return True
