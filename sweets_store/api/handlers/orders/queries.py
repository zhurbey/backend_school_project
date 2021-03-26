import typing as t

from asyncpg import Record  # type: ignore
from asyncpgsa import PG  # type: ignore

from sweets_store.db.tables import orders_table

from .datatypes import OrderCreate


async def create_orders(pg: PG, orders: t.List[OrderCreate]) -> t.List[Record]:

    insert_data = [order_create.dict() for order_create in orders]
    query = orders_table.insert().values(insert_data).returning(orders_table)

    async with pg.transaction() as connection:
        inserted = await connection.fetch(query)

    return t.cast(t.List[Record], inserted)
