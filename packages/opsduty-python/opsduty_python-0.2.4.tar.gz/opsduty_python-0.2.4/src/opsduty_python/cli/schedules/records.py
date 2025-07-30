from datetime import datetime

import pydantic
from opsduty_client.models.schedule_shift_schema import ScheduleShiftSchema


class ScheduleShift(pydantic.BaseModel):
    start: datetime
    end: datetime
    users: list[str]

    @classmethod
    def from_api_response(
        cls, *, schedule_shift: ScheduleShiftSchema
    ) -> "ScheduleShift":
        return cls(
            start=schedule_shift.start,
            end=schedule_shift.end,
            users=[
                f"{user.first_name} {user.last_name}" for user in schedule_shift.users
            ],
        )


class ScheduleShifts(pydantic.BaseModel):
    schedule_id: int
    shifts: list[ScheduleShift]

    @classmethod
    def from_api_response(
        cls, *, schedule_id: int, schedule_shifts: list[ScheduleShiftSchema]
    ) -> "ScheduleShifts":
        return cls(
            schedule_id=schedule_id,
            shifts=[
                ScheduleShift.from_api_response(schedule_shift=shift)
                for shift in schedule_shifts
            ],
        )
