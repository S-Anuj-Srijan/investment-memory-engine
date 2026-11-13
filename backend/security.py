"""Salted scrypt password hashes and opaque, hashed server-side sessions."""
import hashlib
import hmac
import secrets


def hash_password(password):
    if not 12 <= len(password) <= 128:
        raise ValueError('Passwords must contain 12 to 128 characters.')
    salt = secrets.token_hex(16)
    digest = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=16384, r=8, p=1).hex()
    return f'scrypt${salt}${digest}'


def verify_password(password, stored):
    try:
        algorithm, salt, expected = stored.split('$')
        if algorithm != 'scrypt' or len(password) > 128:
            return False
        actual = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=16384, r=8, p=1).hex()
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def token_hash(token):
    return hashlib.sha256(token.encode()).hexdigest()
