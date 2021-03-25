import typing as t

from asyncpgsa import PG  # type: ignore
from asyncpg import Record  # type: ignore

from .datatypes import CourierCreate
from sweets_store.db.tables import couriers_table


async def create_couriers(pg: PG, couriers: t.List[CourierCreate]) -> t.List[Record]:

    insert_data = [courier_create.dict() for courier_create in couriers]
    query = couriers_table.insert().values(insert_data).returning(couriers_table)

    async with pg.transaction() as connection:
        inserted = await connection.fetch(query)

    return t.cast(t.List[Record], inserted)
