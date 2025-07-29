import getpass,bcrypt
from abstract_flask import initialize_call_log
def generate_salt(rounds=None):
    rounds = rounds or 10
    salt = bcrypt.gensalt(rounds=rounds)
    return salt

def verify_password(plaintext_pwd: str, stored_hash: str) -> bool:
    """
    Returns True if plaintext matches the bcrypt stored_hash, else False.
    """
    return bcrypt.checkpw(plaintext_pwd.encode("utf8"),
                          stored_hash.encode("utf8"))


def input_plain_text():
    initialize_call_log()
    plaintext = getpass.getpass("Enter new admin password: ").strip()
    if not plaintext:
        print("✘ Password cannot be empty. Exiting.")
        exit(1)
    return plaintext


def bcrypt_plain_text(plaintext_pwd,rounds=None):
    salt = generate_salt(rounds=rounds)
    plaintext_pwd = plaintext_pwd.encode("utf-8")
    encrypted_bcrypt_hash = bcrypt.hashpw(plaintext_pwd,salt)
    bcrypt_hash = encrypted_bcrypt_hash.decode("utf-8")
    return bcrypt_hash
