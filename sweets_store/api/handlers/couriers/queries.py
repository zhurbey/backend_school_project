import typing as t

from asyncpg import Record  # type: ignore
from asyncpgsa import PG  # type: ignore
from sqlalchemy import func, select, update  # type: ignore

from sweets_store.db.tables import bundles_table, couriers_table, orders_table

from ..base.queries import get_row_by_id, insert_many
from .datatypes import CourierCreateModel
from .utils import get_best_region_average_time


async def create_couriers(pg: PG, couriers: t.List[CourierCreateModel]) -> t.List[Record]:

    return await insert_many(pg, couriers, couriers_table)


async def get_courier_by_id(pg: PG, courier_id: int) -> t.Optional[Record]:

    return await get_row_by_id(pg, courier_id, couriers_table)


async def update_courier(pg: PG, courier_data: t.Dict[str, t.Any]) -> Record:

    query = (
        update(couriers_table)
        .where(couriers_table.c.courier_id == courier_data["courier_id"])
        .values(**courier_data)
        .returning(couriers_table)
    )

    courier_row = await pg.fetchrow(query)
    return courier_row


async def get_courier_rating(pg: PG, courier_id: int) -> float:
    """Return t - min time between average mean times for deliveries in each region"""

    query = (
        select(
            [
                func.array_agg(orders_table.c.complete_time).label("complete_times"),
                func.array_agg(orders_table.c.region).label("regions"),
                bundles_table.c.assign_time.label("assign_time"),
            ]
        )
        .select_from(
            bundles_table.join(orders_table, bundles_table.c.bundle_id == orders_table.c.bundle_id)
        )
        .group_by(bundles_table.c.assign_time)  # group by bundles
        .where(bundles_table.c.courier_id == courier_id)
    )

    bundles_aggregations = await pg.fetch(query)
    return get_best_region_average_time(bundles_aggregations)


async def get_courier_finished_bundles(pg: PG, courier_id: int) -> t.List[Record]:

    query = (
        select([bundles_table.c.courier_type])
        .where(bundles_table.c.is_finished == True)
        .where(bundles_table.c.courier_id == courier_id)
    )

    result = await pg.fetch(query)
    return t.cast(t.List[Record], result)
