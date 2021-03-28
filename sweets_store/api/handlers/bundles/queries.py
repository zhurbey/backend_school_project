import typing as t
from datetime import datetime

from asyncpg import Record  # type: ignore
from asyncpgsa import PG  # type: ignore
from sqlalchemy import select, update  # type: ignore

from sweets_store.db.tables import bundles_table

from ..orders.queries import get_bundle_not_finished_orders, update_orders_bundle


async def create_bundle(pg: PG, courier: Record, orders: t.List[Record]) -> datetime:

    orders_ids = [order["order_id"] for order in orders]
    assign_time = datetime.now()

    bundle_data = {
        "courier_id": courier["courier_id"],
        "courier_type": courier["courier_type"],
        "assign_time": assign_time,
        "is_finished": False,
    }

    bundle_create_query = (
        bundles_table.insert().values(bundle_data).returning(bundles_table.c.bundle_id)
    )

    async with pg.transaction() as connection:

        bundle_id = (await connection.fetchrow(bundle_create_query))["bundle_id"]
        await update_orders_bundle(connection, bundle_id, orders_ids)

    return assign_time


async def get_courier_active_bundle(pg: PG, courier_id: int) -> t.Optional[Record]:

    query = (
        select([bundles_table])
        .where(bundles_table.c.courier_id == courier_id)
        .where(bundles_table.c.is_finished == False)
    )

    return await pg.fetchrow(query)


async def check_if_bundle_is_completed(pg: PG, bundle_id: int) -> bool:

    not_finished_orders = await get_bundle_not_finished_orders(pg, bundle_id)

    return not bool(not_finished_orders)


async def set_bundle_finished_status(pg: PG, bundle_id: int) -> None:

    query = (
        update(bundles_table)
        .where(bundles_table.c.bundle_id == bundle_id)
        .values(is_finished=True)
    )

    await pg.fetch(query)


async def free_orders(pg: PG, orders: t.List[int], bundle_id: int) -> None:

    await update_orders_bundle(pg, None, orders)

    # Check if bundle is empty after freeing not appropriate orders. Mark as finished if so
    if await check_if_bundle_is_completed(pg, bundle_id):
        await set_bundle_finished_status(pg, bundle_id)
