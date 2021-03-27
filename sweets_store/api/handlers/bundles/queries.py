import typing as t
from datetime import datetime

from asyncpg import Record  # type: ignore
from asyncpgsa import PG  # type: ignore
from sqlalchemy import select  # type: ignore

from sweets_store.db.tables import bundles_table, couriers_table

from ..orders.queries import update_orders_bundle


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
