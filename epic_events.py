import click
import jwt
import sys
import sentry_sdk
from common import SECRET_KEY, Base, engine
from user import login, create_user, read_users, update_user, delete_user
from client import create_client, read_clients, update_client, delete_client
from contract import create_contract, read_contracts, update_contract, delete_contract
from event import create_event, read_events, update_event, delete_event

sentry_sdk.init(dsn="https://979957b79bc6e1ab3d1dfe35fb70deb0@o4509594182156288.ingest.de.sentry.io/4509594185171024")


@click.group()
@click.pass_context
def epic_events(ctx):
    if len(sys.argv) > 1 and sys.argv[1] != "login":
        try:
            with open(".token") as f:
                token = f.read()
            current_user = jwt.decode(token, SECRET_KEY, ["HS256"])
            ctx.obj = {"user_id": current_user["id"], "user_role": current_user["role"]}
        except (FileNotFoundError, jwt.InvalidTokenError, jwt.ExpiredSignatureError):
            click.echo("Token not found, invalid or expired, please login again.")
            sys.exit()

epic_events.add_command(login)
epic_events.add_command(create_user)
epic_events.add_command(read_users)
epic_events.add_command(update_user)
epic_events.add_command(delete_user)
epic_events.add_command(create_client)
epic_events.add_command(read_clients)
epic_events.add_command(update_client)
epic_events.add_command(delete_client)
epic_events.add_command(create_contract)
epic_events.add_command(read_contracts)
epic_events.add_command(update_contract)
epic_events.add_command(delete_contract)
epic_events.add_command(create_event)
epic_events.add_command(read_events)
epic_events.add_command(update_event)
epic_events.add_command(delete_event)

if __name__ == '__main__':
    # division_by_zero = 1 / 0
    Base.metadata.create_all(engine)
    epic_events()