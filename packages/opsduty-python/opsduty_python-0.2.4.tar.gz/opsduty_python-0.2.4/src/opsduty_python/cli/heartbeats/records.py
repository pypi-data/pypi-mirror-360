from typing import TypeVar

import pydantic
from opsduty_client.models.cron_heartbeat_state_schema import CronHeartbeatStateSchema
from opsduty_client.models.heartbeat_schema import HeartbeatSchema
from opsduty_client.models.interval_heartbeat_state_schema import (
    IntervalHeartbeatStateSchema,
)
from opsduty_client.types import Unset

V = TypeVar("V")


def raise_on_unset(value: V | Unset) -> V:
    if isinstance(value, Unset):
        raise ValueError("Value is missing.")

    return value


class HeartbeatState(pydantic.BaseModel):
    id: int | None = None
    environment: str | None
    type: str
    muted: bool
    resolve_incident: bool
    timeout_seconds: int

    interval_seconds: int | None = None

    cron_expression: str | None = None
    cron_timezone: str | None = None

    @classmethod
    def from_api_response(
        cls, heartbeat: CronHeartbeatStateSchema | IntervalHeartbeatStateSchema
    ) -> "HeartbeatState":
        return cls(
            id=raise_on_unset(heartbeat.id),
            environment=raise_on_unset(heartbeat.environment),
            type=raise_on_unset(heartbeat.type_),
            muted=raise_on_unset(heartbeat.muted),
            resolve_incident=raise_on_unset(heartbeat.resolve_incident),
            timeout_seconds=raise_on_unset(heartbeat.timeout_seconds),
            # Interval
            interval_seconds=raise_on_unset(
                (
                    heartbeat.interval_seconds
                    if heartbeat.type_ == "interval"
                    and isinstance(heartbeat, IntervalHeartbeatStateSchema)
                    else None
                )
            ),
            # Cron
            cron_expression=raise_on_unset(
                heartbeat.cron_expression
                if heartbeat.type_ == "cron"
                and isinstance(heartbeat, CronHeartbeatStateSchema)
                else None
            ),
            cron_timezone=raise_on_unset(
                heartbeat.cron_timezone
                if heartbeat.type_ == "cron"
                and isinstance(heartbeat, CronHeartbeatStateSchema)
                else None
            ),
        )


class Heartbeat(pydantic.BaseModel):
    id: int | None = None
    heartbeat_id: str | None = None
    name: str
    description: str | None = None
    link: str | None = None
    states: list[HeartbeatState]

    @classmethod
    def from_api_response(cls, heartbeat: HeartbeatSchema) -> "Heartbeat":
        return cls(
            id=raise_on_unset(heartbeat.id),
            heartbeat_id=raise_on_unset(heartbeat.public_primary_key),
            name=raise_on_unset(heartbeat.name),
            description=raise_on_unset(heartbeat.description),
            link=raise_on_unset(heartbeat.link),
            states=[
                HeartbeatState.from_api_response(state) for state in heartbeat.states
            ],
        )


class Heartbeats(pydantic.BaseModel):
    service_id: int
    heartbeats: list[Heartbeat]

    @classmethod
    def from_api_response(
        cls, *, service_id: int, heartbeats: list[HeartbeatSchema]
    ) -> "Heartbeats":
        return cls(
            service_id=service_id,
            heartbeats=[
                Heartbeat.from_api_response(heartbeat) for heartbeat in heartbeats
            ],
        )
