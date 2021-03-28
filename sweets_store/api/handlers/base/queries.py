import typing as t

from asyncpg import Record  # type: ignore
from asyncpgsa import PG  # type: ignore
from pydantic import BaseModel
from sqlalchemy import Table, select  # type: ignore


# Use sequence type for data cause sequence is invariant, list is contravariant
async def insert_many(pg: PG, data: t.Sequence[BaseModel], table: Table) -> t.List[Record]:

    insert_data = [obj_.dict() for obj_ in data]
    query = table.insert().values(insert_data).returning(table)

    inserted = await pg.fetch(query)

    return t.cast(t.List[Record], inserted)


async def get_row_by_id(pg: PG, row_id: int, table: Table) -> t.Optional[Record]:

    # Primary key column
    pk_column = table.primary_key.columns.values()[0]

    query = select([table]).where(pk_column == row_id)
    row = await pg.fetchrow(query)

    return row
