import typing as t

from asyncpg import Record  # type: ignore
from asyncpgsa import PG  # type: ignore
from sqlalchemy import select  # type: ignore

from sweets_store.db.tables import couriers_table

from ..base.queries import get_row_by_id, insert_many
from .datatypes import CourierCreate


async def create_couriers(pg: PG, couriers: t.List[CourierCreate]) -> t.List[Record]:

    return await insert_many(pg, couriers, couriers_table)


async def get_courier_by_id(pg: PG, courier_id: int) -> t.Optional[Record]:

    return await get_row_by_id(pg, courier_id, couriers_table)
