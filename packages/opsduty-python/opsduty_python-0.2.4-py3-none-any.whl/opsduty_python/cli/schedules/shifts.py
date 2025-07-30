import sys
from zoneinfo import ZoneInfo

import click
from opsduty_client.api.schedules import opsduty_api_v1_schedules_list_schedule_shifts

from opsduty_python.cli.utils import (
    FILE_FORMATS,
    FileFormat,
    get_client,
    get_month_from_string,
    render_document,
)

from .records import ScheduleShifts


@click.command(help="List shifts in time period.")
@click.option(
    "--month",
    help=(
        "Specify month (YYYY-MM), default is current month, "
        "which is paid out next month."
    ),
    type=str,
    required=True,
)
@click.option(
    "--timezone", help="Specify the timezone you are in.", type=str, required=True
)
@click.option(
    "--output",
    "-o",
    type=click.Choice(FILE_FORMATS, case_sensitive=False),
    default=str(FileFormat.YAML.value),
    show_default=True,
)
@click.pass_context
def list(ctx: click.Context, month: str, timezone: str, output: str) -> None:
    assert ctx.parent, "Parent command missing"

    schedule_id: int = ctx.parent.params["schedule_id"]
    tz = ZoneInfo(timezone)

    selected_month = get_month_from_string(month=month)
    if not selected_month:
        ctx.fail("Could not parse month.")
        return

    datetime_start = selected_month.first_day.replace(tzinfo=tz)
    datetime_end = selected_month.last_day.replace(tzinfo=tz)

    if not selected_month:
        ctx.fail("Could not parse month.")
        return

    client = get_client(ctx, require_authentication=True)

    shifts = opsduty_api_v1_schedules_list_schedule_shifts.sync(
        schedule_id=schedule_id,
        client=client,
        datetime_start=datetime_start,
        datetime_end=datetime_end,
    )

    if not shifts:
        return

    document = ScheduleShifts.from_api_response(
        schedule_id=schedule_id, schedule_shifts=shifts
    )

    render_document(
        document=document, file_format=FileFormat(output), stream=sys.stdout
    )
