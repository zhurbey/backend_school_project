from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Table  # type: ignore

from ..engine import metadata
from .couriers import CouriersTypesEnum


bundles_table = Table(
    "bundles",
    metadata,
    Column("bundle_id", Integer, primary_key=True),
    Column("courier_id", Integer, ForeignKey("couriers.courier_id"), nullable=False),
    # Courier's type on assign_time moment
    Column("courier_type", CouriersTypesEnum, nullable=False),
    Column("assign_time", DateTime, nullable=False),
    Column("is_finished", Boolean, nullable=False),
)
