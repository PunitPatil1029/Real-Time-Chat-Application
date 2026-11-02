
import hashlib
import secrets
import hmac


def hash_password(password):
    salt = secrets.token_hex(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100000
    ).hex()

    return password_hash, salt


def verify_password(password, stored_hash, salt):
    new_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100000
    ).hex()

    return hmac.compare_digest(new_hash, stored_hash)


if __name__ == "__main__":
    password = "Test123"

    password_hash, salt = hash_password(password)

    print("Password Security Test")
    print("----------------------")
    print("Original Password:", password)
    print("Hashed Password:", password_hash)
    print("Salt:", salt)

    if verify_password(password, password_hash, salt):
        print("Password verification successful!")
    else:
        print("Password verification failed!")
