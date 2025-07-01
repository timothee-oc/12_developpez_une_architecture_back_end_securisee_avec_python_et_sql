from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String
import click
import bcrypt
import jwt
from common import SECRET_KEY, Base, Session, require_roles

ROLES = ["management", "sales", "support"]

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

@click.command()
@click.argument("username")
@click.argument("password")
def login(username: str, password: str):
    with Session() as session:
        user = session.query(User).filter(User.username==username).first()
        if not user or not bcrypt.checkpw(password.encode(), user.password.encode()):
            click.echo("Invalid credentials")
            return
        token = jwt.encode(
            {
                "id": user.id,
                "role": user.role,
                "exp": datetime.now() + timedelta(hours=1)
            },
            SECRET_KEY,
            "HS256"
        )
        with open(".token", "w") as f:
            f.write(token)

@click.command()
@click.argument("username")
@click.argument("password")
@click.argument("role", type=click.Choice(ROLES))
@click.pass_context
@require_roles(["management"])
def create_user(ctx, username, password, role):
    password = hash_password(password)
    with Session() as session:
        user = session.query(User).filter(User.username==username).first()
        if user:
            click.echo("This username is already taken.")
            return
        session.add(
            User(username=username, password=password, role=role)
        )
        session.commit()

@click.command()
def read_users():
    with Session() as session:
        users = session.query(User).all()
        for user in users:
            click.echo(f"{user.id}, {user.username}, {user.role}")

@click.command()
@click.argument("user_id", type=int)
@click.option("--username")
@click.option("--password")
@click.option("--role", type=click.Choice(ROLES))
@click.pass_context
@require_roles(["management"])
def update_user(ctx, user_id: int, username: str, password: str, role: str):
    with Session() as session:
        user = session.query(User).filter(User.id==user_id).first()
        if not user:
            click.echo("No user found with given ID")
            return
        if username and session.query(User).filter(User.username==username).first():
            click.echo("This username is already taken.")
            return
        user.username = username or user.username
        user.password = hash_password(password) if password else user.password
        user.role = role or user.role
        session.add(user)
        session.commit()

@click.command()
@click.argument("user_id", type=int)
@click.pass_context
@require_roles(["management"])
def delete_user(ctx, user_id: int):
    with Session() as session:
        user = session.query(User).filter(User.id==user_id).first()
        if not user:
            click.echo("No user found with given ID")
            return
        session.delete(user)
        session.commit()
