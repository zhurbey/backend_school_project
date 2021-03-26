import typing as t

from pydantic import BaseModel


class OrderCreate(BaseModel):
    order_id: int
    weight: float
    region: int
    delivery_hours: t.List[str]
