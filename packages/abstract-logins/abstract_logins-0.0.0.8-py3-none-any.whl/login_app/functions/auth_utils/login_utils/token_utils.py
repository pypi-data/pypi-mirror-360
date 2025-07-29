import os,datetime,jwt
from abstract_security import get_env_value
JWT_ALGORITHM = "HS256"
JWT_EXP_DELTA_SECONDS = 3600*24
def get_app_secret():
    APP_SECRET = get_env_value("JWT_SECRET")
    if not APP_SECRET:
        raise RuntimeError("JWT_SECRET environment variable is required")
    return APP_SECRET
def get_exp_delta(delta_seconds=None):
    delta_seconds = delta_seconds or JWT_EXP_DELTA_SECONDS
    exp_delta =  datetime.timedelta(seconds=delta_seconds)
    return exp_delta
def get_current_time():
    return datetime.datetime.utcnow()
def get_token_exp(delta_seconds=None):
    exp_delta = get_exp_delta(delta_seconds=delta_seconds)
    current_time = get_current_time()
    exp = current_time + exp_delta
    return exp
# Make a folder named “uploads” parallel to “public”:
def generate_token(username: str, is_admin: bool) -> str:
    import datetime
    exp = get_token_exp()
    payload = { "username": username,
                "is_admin": is_admin,
                "exp": exp }
    app_secret = get_app_secret()
    return jwt.encode(payload, app_secret, algorithm=JWT_ALGORITHM)

def decode_token(token: str) -> dict:
    app_secret = get_app_secret()
    return jwt.decode(token, app_secret, algorithms=[JWT_ALGORITHM])
