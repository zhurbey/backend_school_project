import typing as t
from datetime import datetime

from asyncpg import Record  # type: ignore
from asyncpgsa import PG  # type: ignore
from sqlalchemy import select, update  # type: ignore

from sweets_store.db.tables import bundles_table

from ..orders.queries import get_bundle_not_finished_orders, update_orders_bundle


async def create_bundle(pg: PG, orders: t.List[Record], courier: Record) -> datetime:
    """Create new bundle and assign it new orders. Returns assign_time"""

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
        await update_orders_bundle(connection, orders_ids, bundle_id)

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


async def update_bundle_status(pg: PG, bundle_id: int) -> None:
    """Check if bundle is empty and mark as completed if so"""

    async with pg.transaction() as connection:

        if await check_if_bundle_is_completed(connection, bundle_id):
            await set_bundle_finished_status(connection, bundle_id)


async def release_orders(pg: PG, orders_ids: t.List[int], bundle_id: int) -> None:

    async with pg.transaction() as connection:
        await update_orders_bundle(connection, orders_ids, None)

        # Check if bundle is empty after freeing not appropriate orders. Mark as finished if so
        # Do not use update_bundle_status inside this query to avoid nested transactions
        if await check_if_bundle_is_completed(connection, bundle_id):
            await set_bundle_finished_status(connection, bundle_id)
