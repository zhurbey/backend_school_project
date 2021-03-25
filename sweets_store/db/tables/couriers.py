from sqlalchemy import ARRAY, Column, Enum, Float, Integer, String, Table  # type: ignore

from sweets_store.api.handlers.couriers.constants import CouriersTypes

from ..engine import metadata


CouriersTypesEnum = Enum(CouriersTypes)


couriers_table = Table(
    "couriers",
    metadata,
    Column("courier_id", Integer(), primary_key=True),
    Column("courier_type", CouriersTypesEnum, nullable=False),
    Column("regions", ARRAY(Integer), nullable=False),
    Column("working_hours", ARRAY(String), nullable=False),
    Column("rating", Float()),
    Column("earnings", Integer()),
)
