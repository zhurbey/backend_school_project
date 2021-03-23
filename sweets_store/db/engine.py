import os
import typing as t

from asyncpgsa import PG
from aiohttp.web import Application
from sqlalchemy.ext.declarative import declarative_base
from yarl import URL


db_url = URL.build(
    scheme=os.environ["DB_SCHEME"],
    host=os.environ["DB_HOST"],
    user=os.environ["DB_USER"],
    password=os.environ.get("DB_PASSWORD", ""),
    port=os.environ["DB_PORT"],
    path=os.environ["DB_NAME"],
)

Base = declarative_base()


async def connect_db(app: Application, ) -> None:
    app["pg"] = PG()
    app["pg"].init(str(db_url))


async def disconnect_db(app: Application) -> None:
    app["pg"].close()
