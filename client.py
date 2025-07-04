from datetime import datetime
import click
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from common import Base, Session, require_roles
from user import User
from tabulate import tabulate

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    mail = Column(String)
    phone = Column(String)
    company = Column(String)
    created = Column(DateTime, default=datetime.now)
    updated = Column(DateTime, onupdate=datetime.now)
    contact_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))

@click.command()
@click.option("--name")
@click.option("--mail")
@click.option("--phone")
@click.option("--company")
@click.pass_context
@require_roles(["sales"])
def create_client(ctx, name, mail, phone, company):
    with Session() as session:
        session.add(Client(name=name, mail=mail, phone=phone, company=company, contact_id=ctx.obj["user_id"]))
        session.commit()
    click.echo("Client successfully created")

@click.command()
def read_clients():
    with Session() as session:
        clients = session.query(Client).all()
        columns = [column.name for column in Client.__table__.columns]
        rows = [[getattr(client, col) for col in columns] for client in clients]
        table = tabulate(rows, headers=columns, tablefmt="grid")
        click.echo(table)

@click.command()
@click.argument("client_id", type=int)
@click.option("--name")
@click.option("--mail")
@click.option("--phone")
@click.option("--company")
@click.option("--contact_id", type=int)
@click.pass_context
@require_roles(["sales"])
def update_client(ctx, client_id, name, mail, phone, company, contact_id):
    with Session() as session:
        client = session.query(Client).filter(Client.id==client_id).first()
        if not client:
            click.echo("No client found with given ID")
            return
        if client.contact_id != ctx.obj["user_id"]:
            click.echo("You are not in charge of the client")
            return
        client.name = name or client.name
        client.mail = mail or client.mail
        client.phone = phone or client.phone
        client.company = company or client.company
        if contact_id:
            contact = session.query(User).filter(User.id==contact_id).first()
            if not contact:
                click.echo("No contact found with given ID")
                return
            client.contact_id = contact_id
        session.add(client)
        session.commit()
    click.echo("Client successfully updated")

@click.command()
@click.argument("client_id", type=int)
@click.pass_context
@require_roles(["sales"])
def delete_client(ctx, client_id):
    with Session() as session:
        client = session.query(Client).filter(Client.id==client_id).first()
        if not client:
            click.echo("No client found with given ID")
        session.delete(client)
        session.commit()
    click.echo("Client successfully deleted")
