from sqlalchemy import ARRAY, Column, DateTime, Float, ForeignKey, Integer, String  # type: ignore
from sqlalchemy.orm import relationship  # type: ignore

from ..engine import Base


class Orders(Base):
    __tablename__ = "orders"

    order_id = Column("order_id", Integer(), primary_key=True)
    weight = Column("weight", Float(), nullable=False)
    region = Column("region", Integer(), nullable=False)
    delivery_hours = Column("delivery_hours", ARRAY(String), nullable=False)
    assign_time = Column("assign_type", DateTime())
    complete_time = Column("complete_time", DateTime())

    courier_id = Column("courier_id", Integer(), ForeignKey("couriers.courier_id"))
