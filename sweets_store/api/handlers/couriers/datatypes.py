import typing as t

from pydantic import BaseModel

from .constants import CouriersTypes


class CourierCreate(BaseModel):
    courier_id: int
    courier_type: CouriersTypes
    regions: t.List[int]
    working_hours: t.List[str]
