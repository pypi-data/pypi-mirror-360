import click
import httpx
import structlog
from opsduty_client.api.heartbeats import (
    opsduty_api_v1_heartbeats_healthcheck_environment_checkin,
)
from opsduty_client.errors import UnexpectedStatus

from opsduty_python.cli.mutex import Mutex
from opsduty_python.cli.utils import (
    get_client,
)
from opsduty_python.heartbeats import send_heartbeat_checkin as _send_heartbeat_checkin
from opsduty_python.settings import settings

logger = structlog.get_logger()


class ExitError(click.UsageError):
    def __init__(
        self, message: str, ctx: click.Context | None = None, exit_code: int = 1
    ) -> None:
        super().__init__(message, ctx)
        self.exit_code = exit_code


@click.command(help="Send a heartbeat checkin to OpsDuty.")
@click.option(
    "--heartbeat-id",
    type=str,
    envvar="HEARTBEAT_ID",
    help="Heartbeat ID of the heartbeat you want to checkin.",
    cls=Mutex,
    not_required_if=["service_id", "name"],
)
@click.option(
    "--service-id",
    type=int,
    envvar="SERVICE_ID",
    help=(
        "Use service id and name to lookup heartbeat instead of the "
        "heartbeat id. Authentication required."
    ),
    cls=Mutex,
    not_required_if=["heartbeat_id"],
)
@click.option(
    "--name",
    type=str,
    envvar="NAME",
    help=(
        "Use service id and name to lookup heartbeat instead of the "
        "heartbeat id. Authentication required."
    ),
    cls=Mutex,
    not_required_if=["heartbeat_id"],
)
@click.option(
    "--environment",
    "-e",
    type=str,
    required=False,
    default=None,
    help=(
        "Specify the environment for the heartbeat "
        "(e.g., production, staging, development)."
    ),
    envvar="ENV",
    show_envvar=True,
)
@click.option(
    "--ignore-error",
    type=bool,
    help="Exit with exit code 0, even if the checkin failed.",
    is_flag=True,
    default=False,
)
@click.pass_context
def checkin(
    ctx: click.Context,
    *,
    heartbeat_id: str | None,
    service_id: int | None,
    name: str | None,
    environment: str | None,
    ignore_error: bool,
) -> None:
    if heartbeat_id:
        logger.debug(
            "Sending heartbeat checkin", heartbeat=heartbeat_id, environment=environment
        )

        success = _send_heartbeat_checkin(
            heartbeat=heartbeat_id,
            environment=environment,
            timeout=settings.REQUEST_TIMEOUT,
        )

        if not success:
            exit_code = 0 if ignore_error else 1
            raise ExitError(
                "Could not send heartbeat checkin to OpsDuty.",
                ctx=ctx,
                exit_code=exit_code,
            )

        return

    if service_id and name:
        logger.debug(
            "Sending heartbeat checkin",
            service_id=service_id,
            name=name,
            environment=environment,
        )

        if not environment:
            ctx.fail("Environment is required when --service-id and --name is used.")
            return

        client = get_client(ctx, require_authentication=True)

        try:
            opsduty_api_v1_heartbeats_healthcheck_environment_checkin.sync_detailed(
                client=client, service_id=service_id, name=name, environment=environment
            )
        except (UnexpectedStatus, httpx.TimeoutException) as exc:
            exit_code = 0 if ignore_error else 1
            raise ExitError(
                "Could not send heartbeat checkin to OpsDuty.",
                ctx=ctx,
                exit_code=exit_code,
            ) from exc

        return

    ctx.fail(
        "Either --heartbeat-id or --service-id and --name is required "
        "to lookup heartbeat."
    )
