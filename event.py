import click
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from common import Base, Session, require_roles
from contract import Contract
from user import User

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    start = Column(DateTime)
    end = Column(DateTime)
    location = Column(String)
    attendees = Column(Integer)
    notes = Column(String)
    support_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    contract_id = Column(Integer, ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False)

@click.command()
@click.argument("contract_id", type=int)
@click.option("--name")
@click.option("--start", type=click.DateTime(["%Y-%m-%d"]))
@click.option("--end", type=click.DateTime(["%Y-%m-%d"]))
@click.option("--location")
@click.option("--attendees", type=int)
@click.option("--notes")
@click.option("--support_id", type=int)
@click.pass_context
@require_roles(["sales"])
def create_event(ctx, contract_id, name, start, end, location, attendees, notes, support_id):
    with Session() as session:
        contract = session.query(Contract).filter(Contract.id==contract_id).first()
        if not contract:
            click.echo("No contract found with given ID")
            return
        if contract.client.contact_id != ctx.obj["user_id"]:
            click.echo("You are not in charge of the contract's client")
            return
        if not contract.signed:
            click.echo("This contract is not signed yet.")
            return
        if start and end and start > end:
            click.echo("Start cannot come after end")
            return
        if attendees and attendees < 0:
            click.echo("Attendees cannot have a negative value")
            return
        if support_id:
            support = session.query(User).filter(User.id==support_id).first()
            if not support:
                click.echo("No user found with given ID")
                return

        session.add(Event(name=name, start=start, end=end, location=location, attendees=attendees, notes=notes, support_id=support_id, contract_id=contract_id))
        session.commit()

@click.command()
@click.option("--no-support", is_flag=True)
@click.option("--mine", is_flag=True)
@click.pass_context
def read_events(ctx, no_support, mine):
    with Session() as session:
        query = session.query(Event)
        if no_support:
            query = query.filter(Event.support_id.is_(None))
        if mine:
            query = query.filter(Event.support_id == ctx.obj["user_id"])
        for event in query.all():
            click.echo(event.id, event.name, event.start, event.end, event.location, event.attendees, event.notes, event.contract_id, event.support_id)

@click.command()
@click.argument("event_id", type=int)
@click.option("--name")
@click.option("--start", type=click.DateTime(["%Y-%m-%d"]))
@click.option("--end", type=click.DateTime(["%Y-%m-%d"]))
@click.option("--location")
@click.option("--attendees", type=int)
@click.option("--notes")
@click.option("--support_id", type=int)
@click.pass_context
@require_roles(["management", "support"])
def update_event(ctx, event_id, name, start, end, location, attendees, notes, support_id):
    with Session() as session:
        event = session.query(Event).filter(Event.id==event_id).first()
        if not event:
            click.echo("No event found with given ID")
            return
        if ctx.obj["user_role"] == "support" and event.support_id != ctx.obj["user_id"]:
            click.echo("Youe are not in charge of this event")
            return
        event.name = name or event.name
        if start and start > event.end:
            click.echo("Start cannot come after end")
            return
        event.start = start or event.start
        if end and end < event.start:
            click.echo("Start cannot come after end")
            return
        event.end = end or event.end
        if attendees and attendees < 0:
            click.echo("Attendees cannot have a negative value")
            return
        event.attendees = attendees or event.attendees
        if support_id:
            support = session.query(User).filter(User.id==support_id).first()
            if not support:
                click.echo("No user found with given ID")
                return
            event.support_id = support_id
        event.location = location or event.location
        event.notes = notes or event.notes
        session.add(event)
        session.commit()
        

@click.command()
@click.argument("event_id", type=int)
@click.pass_context
@require_roles(["management"])
def delete_event(ctx, event_id):
    with Session() as session:
        event = session.query(Event).filter(Event.id==event_id).first()
        if not event:
            click.echo("No event found with given ID")
            return
        session.delete(event)
        session.commit()
