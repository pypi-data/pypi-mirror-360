import click

from opsduty_python.cli.cli_groups import LazyGroup
from opsduty_python.settings import Settings, settings
from opsduty_python.utils import logging

# Give us nice and short help parameters, too
CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


@click.version_option()
@click.group(
    context_settings=CONTEXT_SETTINGS,
    epilog="""
Command-line utility for interfacing with OpsDuty.
           """,
)
@click.option(
    "--log-format",
    type=click.Choice(logging.LOG_FORMATS, case_sensitive=False),
    default=str(logging.LogFormat.CONSOLE.value),
    show_default=True,
)
@click.option(
    "--log-level",
    type=click.Choice(logging.LOG_LEVELS, case_sensitive=False),
    default=str(logging.LogLevel.INFO.value),
    show_default=True,
)
@click.option(
    "--base-url",
    type=str,
    default=Settings.field_default("OPSDUTY_BASE_URL"),
    required=False,
    help="Base URL for API requests to OpsDuty.",
)
@click.option(
    "--timeout",
    type=int,
    default=Settings.field_default("REQUEST_TIMEOUT"),
    required=True,
    help="API request timeout to OpsDuty.",
)
@click.option(
    "--access-token",
    type=str,
    default=Settings.field_default("ACCESS_TOKEN"),
    required=False,
    envvar="OPSDUTY_ACCESS_TOKEN",
    show_envvar=True,
    help="Set the bearer token used to communicate with OpsDuty.",
)
@click.pass_context
def opsduty(
    ctx: click.Context,
    log_format: str,
    log_level: str,
    base_url: str,
    timeout: int,
    access_token: str,
) -> None:
    logging.configure_structlog(
        log_level=logging.LogLevel(log_level), log_format=logging.LogFormat(log_format)
    )

    # Initialize settings
    settings.OPSDUTY_BASE_URL = base_url
    settings.REQUEST_TIMEOUT = timeout
    settings.ACCESS_TOKEN = access_token


@click.group(
    cls=LazyGroup,
    lazy_subcommands={
        "checkin": "opsduty_python.cli.heartbeats.checkin.checkin",
        "import": "opsduty_python.cli.heartbeats.import._import",
        "export": "opsduty_python.cli.heartbeats.export.export",
    },
    help="Commands for managing and monitoring heartbeats.",
)
def heartbeats() -> None:
    pass


@click.group(
    cls=LazyGroup,
    lazy_subcommands={
        "shifts": "opsduty_python.cli.schedules.shifts",
    },
    help="Commands for accesing schedules.",
)
def schedules() -> None:
    pass


# Add CLI groups.
opsduty.add_command(heartbeats)
opsduty.add_command(schedules)


if __name__ == "__main__":
    opsduty()
