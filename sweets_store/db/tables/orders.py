from sqlalchemy import (  # type: ignore
    ARRAY,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
)

from ..engine import metadata


orders_table = Table(
    "orders",
    metadata,
    Column("order_id", Integer(), primary_key=True),
    Column("weight", Float(), nullable=False),
    Column("region", Integer(), nullable=False),
    Column("delivery_hours", ARRAY(String), nullable=False),
    Column("assign_type", DateTime()),
    Column("complete_time", DateTime()),
    Column("courier_id", Integer(), ForeignKey("couriers.courier_id")),
)
