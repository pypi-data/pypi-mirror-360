import click

from opsduty_python.cli.cli_groups import LazyGroup


@click.group(
    cls=LazyGroup,
    lazy_subcommands={
        "list": "opsduty_python.cli.schedules.shifts.list",
    },
    help="Commands for accesing shifts in a schedule.",
)
@click.option(
    "--schedule-id",
    type=int,
    required=True,
    help="The ID of the schedule to lookup data from.",
)
def shifts(*, schedule_id: int) -> None:
    pass
