import typing as t
from datetime import datetime

from asyncpg import Record  # type: ignore
from asyncpgsa import PG  # type: ignore
from sqlalchemy import select, update  # type: ignore

from sweets_store.db.tables import bundles_table, orders_table

from ..base.queries import insert_many
from .datatypes import OrderCreateModel


async def create_orders(pg: PG, orders: t.List[OrderCreateModel]) -> t.List[Record]:

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


async def update_orders_bundle(
    pg: PG, bundle_id: t.Optional[int], orders_ids: t.List[int]
) -> None:

    """Bind orders from orders_ids to bundle_id"""

    query = (
        update(orders_table)
        .where(orders_table.c.order_id.in_(orders_ids))
        .values(bundle_id=bundle_id)
    )

    await pg.fetch(query)


async def set_order_complete_time(pg: PG, order_id: int, complete_time: datetime) -> int:
    """Mark order as completed and return bundle id"""

    query = (
        update(orders_table)
        .where(orders_table.c.order_id == order_id)
        .values(complete_time=complete_time)
        .returning(orders_table.c.bundle_id)
    )

    bundle_id_row = await pg.fetchrow(query)

    return t.cast(int, bundle_id_row["bundle_id"])


async def get_order_courier_id(pg: PG, order_id: int) -> t.Optional[int]:
    """Returns courier_id for order_id, only returns a pair if there's a matching pair"""

    query = (
        select([bundles_table.c.courier_id])
        .select_from(
            bundles_table.join(orders_table, bundles_table.c.bundle_id == orders_table.c.bundle_id)
        )
        .where(orders_table.c.order_id == order_id)
    )

    courier_id_row = await pg.fetchrow(query)

    result = courier_id_row["courier_id"] if courier_id_row else courier_id_row
    return t.cast(t.Optional[int], result)


async def is_order_completed(pg: PG, order_id: int) -> t.Optional[datetime]:
    """Returns complete_time if completed, None otherwise"""

    query = select([orders_table.c.complete_time]).where(orders_table.c.order_id == order_id)

    complete_time_row = await pg.fetchrow(query)

    result = complete_time_row["complete_time"] if complete_time_row else complete_time_row
    return t.cast(t.Optional[datetime], result)
