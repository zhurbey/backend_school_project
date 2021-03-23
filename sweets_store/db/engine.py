import os
import typing as t

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from yarl import URL


db_url = URL.build(
    scheme=os.environ["DB_SCHEME"],
    host=os.environ["DB_HOST"],
    user=os.environ["DB_USER"],
    password=os.environ.get("DB_PASSWORD", ""),
    port=os.environ["DB_PORT"],
    path=os.environ["DB_NAME"],
)

engine = create_engine(str(db_url))
Base = declarative_base()

Session = sessionmaker(bind=engine)
