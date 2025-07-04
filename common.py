from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import click
from functools import wraps
from dotenv import load_dotenv
import os
import sentry_sdk

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("Secret key for login token is not set in .env file")

SENTRY_DSN = os.getenv("SENTRY_DSN")
if not SENTRY_DSN:
    raise ValueError("DSN is not set in the .env file")
sentry_sdk.init(dsn=SENTRY_DSN, send_default_pii=True)

Base = declarative_base()
engine = create_engine("sqlite:///epic_events.db")
Session = sessionmaker(engine)

def require_roles(roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if args[0].obj["user_role"] not in roles:
                click.echo("Access forbidden !")
                return
            return f(*args, **kwargs)
        return wrapper
    return decorator
