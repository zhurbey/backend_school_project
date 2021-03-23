from sqlalchemy import ARRAY, Column, Enum, Float, Integer, String  # type: ignore
from sqlalchemy.orm import relationship

from sweets_store.api.handlers.couriers.constants import CouriersTypes

from ..engine import Base


class Couriers(Base):
    __tablename__ = "couriers"

    courier_id = Column("courier_id", Integer(), primary_key=True)
    courier_type = Column("courier_type", Enum(CouriersTypes), nullable=False)
    regions = Column("regions", ARRAY(Integer), nullable=False)
    working_hours = Column("working_hours", ARRAY(String), nullable=False)
    rating = Column("rating", Float())
    earnings = Column("earnings", Integer())

    orders = relationship("Orders", backref="courier")
