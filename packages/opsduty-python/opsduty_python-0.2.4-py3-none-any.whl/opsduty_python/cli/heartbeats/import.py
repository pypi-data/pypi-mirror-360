from typing import TextIO

import click
from opsduty_client.api.heartbeats import (
    opsduty_api_v1_heartbeats_create_heartbeat,
    opsduty_api_v1_heartbeats_create_heartbeat_state,
    opsduty_api_v1_heartbeats_delete_heartbeat,
    opsduty_api_v1_heartbeats_delete_heartbeat_state,
    opsduty_api_v1_heartbeats_update_heartbeat,
    opsduty_api_v1_heartbeats_update_heartbeat_state,
)
from opsduty_client.client import AuthenticatedClient
from opsduty_client.models.create_heartbeat_input import CreateHeartbeatInput
from opsduty_client.models.create_heartbeat_state_input import CreateHeartbeatStateInput
from opsduty_client.models.cron_heartbeat_state_schema import CronHeartbeatStateSchema
from opsduty_client.models.heartbeat_schema import HeartbeatSchema
from opsduty_client.models.heartbeat_type import HeartbeatType
from opsduty_client.models.interval_heartbeat_state_schema import (
    IntervalHeartbeatStateSchema,
)
from opsduty_client.models.update_heartbeat_input import UpdateHeartbeatInput
from opsduty_client.models.update_heartbeat_state_input import UpdateHeartbeatStateInput
from structlog import get_logger

from opsduty_python.cli.utils import (
    get_client,
    parse_document,
)

from .export import fetch_heartbeats
from .records import Heartbeat, Heartbeats, HeartbeatState

logger = get_logger()


@click.command(
    help="Import heartbeats from a definition file containing heartbeat data."
)
@click.option(
    "--file",
    "-f",
    type=click.File(mode="r"),
    required=True,
    help=(
        "Heartbeat definition file to import. This file should be on the same "
        "format as the export command use."
    ),
)
@click.option(
    "--remove-unknown-heartbeats/--keep-unknown-heartbeats",
    type=bool,
    help=(
        "Remove any heartbeats or heartbeat states that is not defined "
        "in the input document."
    ),
    is_flag=True,
    default=False,
)
@click.option(
    "--confirm",
    type=bool,
    help=(
        "The confirm flag is required when the script wants "
        "to delete configuration in OpsDuty."
    ),
    is_flag=True,
    default=False,
)
@click.option(
    "--dry-run",
    type=bool,
    help="The CLI is not going to apply any changes to OpsDuty if enabled.",
    is_flag=True,
    default=False,
)
@click.pass_context
def _import(
    ctx: click.Context,
    *,
    file: TextIO,
    remove_unknown_heartbeats: bool,
    confirm: bool,
    dry_run: bool,
) -> None:
    if remove_unknown_heartbeats and not confirm:
        ctx.fail("--confirm is required when --remove-unknown-heartbeats is used.")
        return

    client = get_client(ctx, require_authentication=True)

    document = parse_document(file, Heartbeats)
    existing_heartbeats = fetch_heartbeats(
        client=client, service_id=document.service_id
    )

    matched_heartbeats, new_heartbeats, unknown_heartbeats = _match_heartbeats(
        document.heartbeats, existing_heartbeats
    )

    logger.info(
        f"Matched {len(matched_heartbeats)} existing heartbeats, "
        f"found {len(new_heartbeats)} new heartbeats."
    )
    if unknown_heartbeats:
        logger.warning(
            f"{len(unknown_heartbeats)} unknown heartbeats exists in OpsDuty."
        )

    # Create new heartbeats
    _create_heartbeats(
        client=client,
        new_heartbeats=new_heartbeats,
        service_id=document.service_id,
        dry_run=dry_run,
    )

    # Update and existing heartbeats
    _update_heartbeats(
        client=client,
        matched_heartbeats=matched_heartbeats,
        service_id=document.service_id,
        dry_run=dry_run,
    )

    # Remove unknown heartbeats
    if remove_unknown_heartbeats and confirm:
        _remove_unknown_heartbeats(
            client=client, unknown_heartbeats=unknown_heartbeats, dry_run=dry_run
        )


def _match_heartbeats(
    input: list[Heartbeat], existing_heartbeats: list[HeartbeatSchema]
) -> tuple[
    list[tuple[Heartbeat, HeartbeatSchema]], list[Heartbeat], list[HeartbeatSchema]
]:
    """
    Match existing heartbeats with the input.
    """
    matched_heartbeats: list[tuple[Heartbeat, HeartbeatSchema]] = []
    new_heartbeats: list[Heartbeat] = []
    seen_existing_heartbeat_ids: set[int] = set()

    existing_by_id = {heartbeat.id: heartbeat for heartbeat in existing_heartbeats}
    existing_by_heartbeat_id = {
        heartbeat.public_primary_key: heartbeat for heartbeat in existing_heartbeats
    }
    existing_by_name = {heartbeat.name: heartbeat for heartbeat in existing_heartbeats}

    for heartbeat in input:
        existing_heartbeat: HeartbeatSchema | None = None

        if heartbeat.id and heartbeat.id in existing_by_id:
            existing_heartbeat = existing_by_id[heartbeat.id]
        elif (
            heartbeat.heartbeat_id
            and heartbeat.heartbeat_id in existing_by_heartbeat_id
        ):
            existing_heartbeat = existing_by_heartbeat_id[heartbeat.heartbeat_id]
        elif heartbeat.name and heartbeat.name in existing_by_name:
            existing_heartbeat = existing_by_name[heartbeat.name]

        if existing_heartbeat:
            matched_heartbeats.append((heartbeat, existing_heartbeat))
            assert existing_heartbeat.id
            seen_existing_heartbeat_ids.add(existing_heartbeat.id)
        else:
            new_heartbeats.append(heartbeat)

    assert len(matched_heartbeats) + len(new_heartbeats) == len(input)

    unknown_heartbeats: list[HeartbeatSchema] = []

    for existing_heartbeat in existing_heartbeats:
        if existing_heartbeat.id not in seen_existing_heartbeat_ids:
            unknown_heartbeats.append(existing_heartbeat)

    return matched_heartbeats, new_heartbeats, unknown_heartbeats


def _match_heartbeat_states(
    input: list[HeartbeatState],
    existing_heartbeat_states: list[
        CronHeartbeatStateSchema | IntervalHeartbeatStateSchema
    ],
) -> tuple[
    list[
        tuple[HeartbeatState, CronHeartbeatStateSchema | IntervalHeartbeatStateSchema]
    ],
    list[HeartbeatState],
    list[CronHeartbeatStateSchema | IntervalHeartbeatStateSchema],
]:
    """
    Match existing heartbeats with the input.
    """

    matched_heartbeat_states: list[
        tuple[HeartbeatState, CronHeartbeatStateSchema | IntervalHeartbeatStateSchema]
    ] = []
    new_heartbeat_states: list[HeartbeatState] = []
    seen_existing_heartbeat_state_ids: set[int] = set()

    existing_by_id = {state.id: state for state in existing_heartbeat_states}
    existing_by_environment = {
        state.environment: state for state in existing_heartbeat_states
    }

    for state in input:
        existing_state: (
            CronHeartbeatStateSchema | IntervalHeartbeatStateSchema | None
        ) = None

        if state.id and state.id in existing_by_id:
            existing_state = existing_by_id[state.id]
        elif state.environment and state.environment in existing_by_environment:
            existing_state = existing_by_environment[state.environment]

        if existing_state:
            matched_heartbeat_states.append((state, existing_state))
            assert existing_state.id
            seen_existing_heartbeat_state_ids.add(existing_state.id)
        else:
            new_heartbeat_states.append(state)

    assert len(matched_heartbeat_states) + len(new_heartbeat_states) == len(input)

    unknown_heartbeat_states: list[
        CronHeartbeatStateSchema | IntervalHeartbeatStateSchema
    ] = []

    for existing_heartbeat_state in existing_heartbeat_states:
        if existing_heartbeat_state.id not in seen_existing_heartbeat_state_ids:
            unknown_heartbeat_states.append(existing_heartbeat_state)

    return matched_heartbeat_states, new_heartbeat_states, unknown_heartbeat_states


#
# Heartbeat states
#


def _create_heartbeat_states(
    *,
    client: AuthenticatedClient,
    new_heartbeat_states: list[HeartbeatState],
    heartbeat_id: int,
    dry_run: bool,
) -> None:
    for heartbeat_state in new_heartbeat_states:
        if not heartbeat_state.environment:
            return

        logger.info(
            f"Creating heartbeat state for environment {heartbeat_state.environment}."
        )

        if not dry_run:
            opsduty_api_v1_heartbeats_create_heartbeat_state.sync(
                client=client,
                body=CreateHeartbeatStateInput(
                    heartbeat_id=heartbeat_id,
                    environment=heartbeat_state.environment,
                    type_=HeartbeatType(heartbeat_state.type),
                    cron_expression=heartbeat_state.cron_expression,
                    cron_timezone=heartbeat_state.cron_timezone,
                    interval_seconds=heartbeat_state.interval_seconds,
                    timeout_seconds=heartbeat_state.timeout_seconds,
                    muted=heartbeat_state.muted,
                    resolve_incident=heartbeat_state.resolve_incident,
                ),
            )


def _update_heartbeat_states(
    *,
    client: AuthenticatedClient,
    matched_heartbeat_states: list[
        tuple[HeartbeatState, CronHeartbeatStateSchema | IntervalHeartbeatStateSchema]
    ],
    dry_run: bool,
) -> None:
    """Update any existing heartbeat states."""

    heartbeat_state_fields = [
        "type",
        "cron_expression",
        "cron_timezone",
        "interval_seconds",
        "timeout_seconds",
        "muted",
        "resolve_incident",
    ]

    for expected_heartbeat_state, existing_heartbeat_state in matched_heartbeat_states:
        if not existing_heartbeat_state.id:
            continue

        if expected_heartbeat_state.environment != existing_heartbeat_state.environment:
            logger.warning(
                f"Cannot change heartbeat state environment after it is created. "
                f"Heartbeat state id {existing_heartbeat_state.id}, current "
                f"environment {existing_heartbeat_state.environment}."
            )

        changed = False
        for field in heartbeat_state_fields:
            if getattr(expected_heartbeat_state, field, None) != getattr(
                existing_heartbeat_state, field, None
            ):
                changed = True
                break

        if changed:
            logger.info(
                f"Updating heartbeat state {existing_heartbeat_state.environment} "
                f"({existing_heartbeat_state.id})"
            )

            if not dry_run:
                opsduty_api_v1_heartbeats_update_heartbeat_state.sync(
                    heartbeat_state_id=existing_heartbeat_state.id,
                    client=client,
                    body=UpdateHeartbeatStateInput(
                        type_=HeartbeatType(expected_heartbeat_state.type),
                        cron_expression=expected_heartbeat_state.cron_expression,
                        cron_timezone=expected_heartbeat_state.cron_timezone,
                        interval_seconds=expected_heartbeat_state.interval_seconds,
                        timeout_seconds=expected_heartbeat_state.timeout_seconds,
                        muted=expected_heartbeat_state.muted,
                        resolve_incident=expected_heartbeat_state.resolve_incident,
                    ),
                )


def _remove_unknown_heartbeat_states(
    *,
    client: AuthenticatedClient,
    unknown_heartbeat_states: list[
        CronHeartbeatStateSchema | IntervalHeartbeatStateSchema
    ],
    dry_run: bool,
) -> None:
    """
    Remove unknown heartbeat states from the provided list.
    """

    for heartbeat_state in unknown_heartbeat_states:
        if not heartbeat_state.id:
            continue

        logger.info(
            f"Removing unknown heartbeat state {heartbeat_state.environment} "
            f"({heartbeat_state.id})"
        )

        if not dry_run:
            opsduty_api_v1_heartbeats_delete_heartbeat_state.sync_detailed(
                heartbeat_state_id=heartbeat_state.id, client=client
            )


#
# Heartbeats
#


def _create_heartbeats(
    *,
    client: AuthenticatedClient,
    new_heartbeats: list[Heartbeat],
    service_id: int,
    dry_run: bool,
) -> None:
    """Create all heartbeats and heartbeat states in the provided list."""

    for heartbeat in new_heartbeats:
        logger.info(f"Creating heartbeat {heartbeat.name}")

        if not dry_run:
            new_heartbeat = opsduty_api_v1_heartbeats_create_heartbeat.sync(
                client=client,
                body=CreateHeartbeatInput(
                    name=heartbeat.name,
                    description=heartbeat.description or "",
                    link=heartbeat.link,
                    service=service_id,
                ),
            )

            assert new_heartbeat
            assert new_heartbeat.id

            for state in heartbeat.states:
                _create_heartbeat_states(
                    client=client,
                    new_heartbeat_states=[state],
                    heartbeat_id=new_heartbeat.id,
                    dry_run=dry_run,
                )


def _update_heartbeats(
    *,
    client: AuthenticatedClient,
    matched_heartbeats: list[tuple[Heartbeat, HeartbeatSchema]],
    service_id: int,
    dry_run: bool,
) -> None:
    """Update any existing heartbeats."""

    heartbeat_fields = ["name", "description", "link"]

    for expected_heartbeat, existing_heartbeat in matched_heartbeats:
        if not existing_heartbeat.id:
            continue

        changed = False
        for field in heartbeat_fields:
            if getattr(expected_heartbeat, field) != getattr(existing_heartbeat, field):
                changed = True
                break

        if changed:
            logger.info(
                f"Updating heartbeat {existing_heartbeat.name} "
                f"({existing_heartbeat.id})"
            )

            if not dry_run:
                opsduty_api_v1_heartbeats_update_heartbeat.sync(
                    heartbeat_id=existing_heartbeat.id,
                    client=client,
                    body=UpdateHeartbeatInput(
                        name=expected_heartbeat.name,
                        description=expected_heartbeat.description or "",
                        link=expected_heartbeat.link,
                        service=service_id,
                    ),
                )

        matched_heartbeat_states, new_heartbeat_states, unknown_heartbeat_states = (
            _match_heartbeat_states(
                expected_heartbeat.states, existing_heartbeat.states
            )
        )

        logger.info(
            f"Matched {len(matched_heartbeat_states)} existing heartbeat states, "
            f"found {len(new_heartbeat_states)} new heartbeat states."
        )
        if unknown_heartbeat_states:
            logger.warning(
                f"{len(unknown_heartbeat_states)} unknown "
                f"heartbeat states exists in OpsDuty."
            )

        # Create new heartbeats
        _create_heartbeat_states(
            client=client,
            new_heartbeat_states=new_heartbeat_states,
            heartbeat_id=existing_heartbeat.id,
            dry_run=dry_run,
        )

        # Update and existing heartbeats
        _update_heartbeat_states(
            client=client,
            matched_heartbeat_states=matched_heartbeat_states,
            dry_run=dry_run,
        )

        # Remove unknown heartbeats
        _remove_unknown_heartbeat_states(
            client=client,
            unknown_heartbeat_states=unknown_heartbeat_states,
            dry_run=dry_run,
        )


def _remove_unknown_heartbeats(
    *,
    client: AuthenticatedClient,
    unknown_heartbeats: list[HeartbeatSchema],
    dry_run: bool,
) -> None:
    """
    Remove unknown heartbeats from the provided list.
    """

    for heartbeat in unknown_heartbeats:
        if not heartbeat.id:
            continue

        logger.info(f"Removing unknown heartbeat {heartbeat.name} ({heartbeat.id})")

        if not dry_run:
            opsduty_api_v1_heartbeats_delete_heartbeat.sync_detailed(
                heartbeat_id=heartbeat.id, client=client
            )
