import typing as t

from pydantic import BaseModel, confloat, validator

from sweets_store.utils.dates import pydantic_match_hours_interval_validator


class OrderCreate(BaseModel):
    order_id: int
    weight: confloat(le=150, ge=0.01)  # type: ignore
    region: int
    delivery_hours: t.List[str]

    _match_hours_interval = validator("delivery_hours", allow_reuse=True, each_item=True)(
        pydantic_match_hours_interval_validator
    )
