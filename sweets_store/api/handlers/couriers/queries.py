import typing as t

from asyncpg import Record  # type: ignore
from asyncpgsa import PG  # type: ignore

from sweets_store.db.tables import couriers_table

from .datatypes import CourierCreate


async def create_couriers(pg: PG, couriers: t.List[CourierCreate]) -> t.List[Record]:

    insert_data = [courier_create.dict() for courier_create in couriers]
    query = couriers_table.insert().values(insert_data).returning(couriers_table)

    async with pg.transaction() as connection:
        inserted = await connection.fetch(query)

    return t.cast(t.List[Record], inserted)
