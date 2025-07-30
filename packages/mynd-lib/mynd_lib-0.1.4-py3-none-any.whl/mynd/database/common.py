"""Module with database functionality for Mynds ORM."""

import typing

import sqlalchemy as sqla
import sqlmodel as sqlm
import sqlalchemy.ext.asyncio as sqlasync

import mynd.utils.env as env


Engine: typing.TypeAlias = sqla.Engine
Session: typing.TypeAlias = sqlm.Session


def create_engine(
    name: str,
    host: str,
    port: int,
    username: str | None = None,
    password: str | None = None,
    **kwargs,
) -> Engine:
    """Creates a SQL database engine."""

    if not username:
        username: str = env.get_value("PG_USERNAME")
    if not password:
        password: str = env.get_value("PG_PASSWORD")

    assert username is not None, "username not provided"
    assert password is not None, "password not provided"

    # NOTE: We only support postgresql databases for now
    url: str = f"postgresql+psycopg://{username}:{password}@{host}:{port}/{name}"
    engine: sqla.Engine = sqlm.create_engine(url, **kwargs)
    return engine


def verify_engine(engine: Engine) -> None | str:
    """Verifies if a database engine is able to connect."""
    try:
        connection: sqla.Connection = engine.connect()
        connection.close()
        return None
    except sqla.exc.SQLAlchemyError as error:
        return str(error)
