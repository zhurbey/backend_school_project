import typing as t

from pydantic import BaseModel, validator

from sweets_store.utils.dates import pydantic_match_hours_interval_validator

from .constants import CouriersTypes


class CourierCreate(BaseModel):
    courier_id: int
    courier_type: CouriersTypes
    regions: t.List[int]
    working_hours: t.List[str]

    _match_hours_interval = validator("working_hours", allow_reuse=True, each_item=True)(
        pydantic_match_hours_interval_validator
    )


class CourierPatch(BaseModel):
    courier_id: int
    courier_type: t.Optional[CouriersTypes]
    regions: t.Optional[t.List[int]]
    working_hours: t.Optional[t.List[str]]

    _match_hours_interval = validator("working_hours", allow_reuse=True, each_item=True)(
        pydantic_match_hours_interval_validator
    )
