import typing as t

from asyncpg import Record  # type: ignore
from asyncpgsa import PG  # type: ignore
from sqlalchemy import select, update  # type: ignore

from sweets_store.db.tables import couriers_table, orders_table

from ..base.queries import insert_many
from .datatypes import OrderCreate


async def create_orders(pg: PG, orders: t.List[OrderCreate]) -> t.List[Record]:

    return await insert_many(pg, orders, orders_table)


async def get_free_orders(pg: PG) -> t.List[Record]:
    """Return orders which are not finished and not bounded to any bundle"""

    query = select([orders_table]).where(orders_table.c.bundle_id == None)
    orders = await pg.fetch(query)

    return t.cast(t.List[Record], orders)


async def get_bundle_not_finished_orders(pg: PG, bundle_id: int) -> t.List[Record]:

    query = (
        select([orders_table])
        .where(orders_table.c.bundle_id == bundle_id)
        .where(orders_table.c.complete_time == None)
    )

    orders = await pg.fetch(query)

    return t.cast(t.List[Record], orders)


async def update_orders_bundle(pg: PG, bundle_id: int, orders_ids: t.List[int]) -> None:
    """Bind orders from orders_ids to bundle_id"""

    query = (
        update(orders_table)
        .where(orders_table.c.order_id.in_(orders_ids))
        .values(bundle_id=bundle_id)
    )

    await pg.fetch(query)
