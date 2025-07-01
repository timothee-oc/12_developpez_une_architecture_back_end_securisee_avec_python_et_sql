from datetime import datetime
import click
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Float, Boolean
from sqlalchemy.orm import relationship
from common import Base, Session, require_roles
from client import Client

class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True)
    total_amount = Column(Float)
    due_amount = Column(Float)
    created = Column(DateTime, default=datetime.now)
    signed = Column(Boolean, default=False)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    client = relationship("Client")

@click.command()
@click.argument("client_id", type=int)
@click.option("--total_amount", type=float)
@click.option("--due_amount", type=float)
@click.option("--signed/--no-signed", default=True)
@click.pass_context
@require_roles(["management"])
def create_contract(ctx, client_id, total_amount, due_amount, signed):
    with Session() as session:
        client = session.query(Client).filter(Client.id==client_id).first()
        if not client:
            click.echo("No client found with given ID")
            return
        if total_amount and total_amount < 0:
            click.echo("Total amount cannot be negative")
            return
        if due_amount and due_amount > total_amount:
            click.echo("Due amount cannot be greater than total amount")
            return
        session.add(Contract(total_amount=total_amount, due_amount=total_amount, signed=signed, client_id=client_id))
        session.commit()

@click.command()
@click.option("--not-signed", is_flag=True)
@click.option("--not-payed", is_flag=True)
def read_contracts(not_signed, not_payed):
    with Session() as session:
        query = session.query(Contract)
        if not_signed:
            query = query.filter(Contract.signed.is_(False))
        if not_payed:
            query = query.filter(Contract.due_amount > 0)
        for contract in query.all():
            print(contract.id, contract.total_amount, contract.due_amount, contract.created, contract.signed, contract.client_id)

@click.command()
@click.argument("contract_id", type=int)
@click.option("--total_amount", type=float)
@click.option("--due_amount", type=float)
@click.option("--signed/--no-signed", default=True)
@click.pass_context
@require_roles(["management", "sales"])
def update_contract(ctx, contract_id, total_amount, due_amount, signed):
    with Session() as session:
        contract = session.query(Contract).filter(Contract.id==contract_id).first()
        if not contract:
            click.echo("No contract found with given ID")
            return
        if ctx.obj["user_role"] == "sales" and contract.client.contact_id != ctx.obj["user_id"]:
            click.echo("You are not in charge of this contract's client")
            return
        if total_amount and total_amount < 0:
            click.echo("Total amount cannot be negative")
            return
        contract.total_amount = total_amount or contract.total_amount
        if due_amount and due_amount > contract.total_amount:
            click.echo("Due amount cannot be greater than total amount")
            return
        contract.due_amount = due_amount or contract.due_amount
        contract.signed = signed
        session.add(contract)
        session.commit()
        

@click.command()
@click.argument("contract_id", type=int)
@click.pass_context
@require_roles(["management"])
def delete_contract(ctx, contract_id):
    with Session() as session:
        contract = session.query(Contract).filter(Contract.id==contract_id).first()
        if not contract:
            click.echo("No contract found with given ID")
        session.delete(contract)
        session.commit()
