import sys

import click
from opsduty_client.api.heartbeats import opsduty_api_v1_heartbeats_list_heartbeats
from opsduty_client.client import AuthenticatedClient
from opsduty_client.models.heartbeat_schema import HeartbeatSchema

from opsduty_python.cli.utils import (
    FILE_FORMATS,
    FileFormat,
    get_client,
    render_document,
)

from .records import Heartbeats


@click.command(
    help="Export heartbeats from OpsDuty to definition file containing heartbeat data."
)
@click.option(
    "--service-id",
    type=int,
    required=True,
    help="The ID of the service to which the heartbeats belong.",
)
@click.option(
    "--output",
    "-o",
    type=click.Choice(FILE_FORMATS, case_sensitive=False),
    default=str(FileFormat.YAML.value),
    show_default=True,
)
@click.pass_context
def export(ctx: click.Context, *, service_id: int, output: str) -> None:
    client = get_client(ctx, require_authentication=True)

    existing_heartbeats = fetch_heartbeats(client=client, service_id=service_id)
    document = Heartbeats.from_api_response(
        service_id=service_id, heartbeats=existing_heartbeats
    )

    render_document(
        document=document, file_format=FileFormat(output), stream=sys.stdout
    )


def fetch_heartbeats(
    client: AuthenticatedClient, service_id: int
) -> list[HeartbeatSchema]:
    has_next_page = True
    cursor: str | None = None

    heartbeats: list[HeartbeatSchema] = []

    while has_next_page:
        page = opsduty_api_v1_heartbeats_list_heartbeats.sync(
            client=client, service=service_id, after=cursor
        )
        assert page

        has_next_page = page.page_info.has_next_page
        cursor = page.page_info.end_cursor if page.page_info.end_cursor else None

        heartbeats.extend(page.items)

    return heartbeats
