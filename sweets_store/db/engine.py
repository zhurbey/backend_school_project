import os

from aiohttp.web import Application
from asyncpgsa import PG  # type: ignore
from sqlalchemy import MetaData  # type: ignore
from yarl import URL


db_url = URL.build(
    scheme=os.environ["DB_SCHEME"],
    host=os.environ["DB_HOST"],
    user=os.environ["DB_USER"],
    password=os.environ.get("DB_PASSWORD", ""),
    port=int(os.environ["DB_PORT"]),
    path=os.environ["DB_NAME"],
)

metadata = MetaData()


async def connect_db(app: Application) -> None:

    app["pg"] = PG()
    await app["pg"].init(str(db_url))


async def disconnect_db(app: Application) -> None:
    await app["pg"].pool.close()
