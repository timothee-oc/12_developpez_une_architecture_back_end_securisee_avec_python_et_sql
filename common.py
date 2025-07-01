from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import click
from functools import wraps

SECRET_KEY = "hyper_secret_key"
DATABASE_URL = "sqlite:///epic_events.db"

Base = declarative_base()
engine = create_engine(DATABASE_URL)
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
