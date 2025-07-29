"""Database utilities."""
import sqlalchemy as sql
import sqlalchemy.orm
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql.expression import Executable
from collections import namedtuple
from collections.abc import Sequence, Iterable, Mapping, Collection
from typing import Any, Optional
import pandas as pd

from globsync.utils.logging import log


# BaseRow type and accompanying utilities


class BaseRow(DeclarativeBase):
    """Base class for rows of a database table."""

    pass


def convert[T: BaseRow](row: T | tuple | dict, Target: type[T] | type[tuple] | type[dict]) -> T | tuple | dict | None:
    """Convert back and forth between a SQL Table rows and some basic Python types."""
    if isinstance(row, BaseRow):
        columns = [attr.name for attr in sql.inspect(type(row)).columns]
        if Target is tuple:
            return namedtuple(type(row).__name__, columns)(*[getattr(row, column) for column in columns])
        elif Target is dict:
            return {column: getattr(row, column) for column in columns}
    elif not issubclass(Target, (tuple, dict)):
        columns = [attr.name for attr in sql.inspect(Target).columns]
        if isinstance(row, tuple):
            if hasattr(row, '_fields'):
                return Target(**{column: getattr(row, column, None) for column in columns})
            else:
                if len(row) == len(columns):
                    return Target(**{column: value for column, value in zip(columns, row)})
        elif isinstance(row, dict):
            return Target(**{column: row.get(column, None) for column in columns})
    raise NotImplementedError


def add_rows(db: str, rows: Collection[BaseRow]) -> None:
    """Add rows to a table in the database."""
    if len(rows) == 0:
        return
    engine = sql.create_engine(db)
    inspector = sql.inspect(engine)
    # BaseRow.metadata.create_all(engine)
    with sql.orm.sessionmaker(engine).begin() as session:
        for row in rows:
            if not inspector.has_table(type(row).__tablename__):
                type(row).__table__.create(engine)
            session.add(row)


def add_row(db: str, row: BaseRow) -> None:
    """Add a row to a table in the database."""
    add_rows(db, [row])


def rm_rows(db: str, Row: type[BaseRow], primary_keys: Collection[tuple | dict]) -> None:
    """Remove rows from a table in the database."""
    if len(primary_keys) == 0:
        return
    engine = sql.create_engine(db)
    inspector = sql.inspect(engine)
    if not inspector.has_table(Row.__tablename__):
        log("warning", f'No "{Row.__tablename__}" table found in the database.')
        return
    with sql.orm.sessionmaker(engine).begin() as session:
        for primary_key in primary_keys:
            row = session.get(Row, primary_key)
            if row is None:
                log("warning", f'Row with primary key "{primary_key}" not present in "{Row.__tablename__}" table')
            else:
                session.delete(row)


def rm_row(db: str, Row: type[BaseRow], primary_key: tuple | dict) -> None:
    """Remove a row from a table in the database."""
    rm_rows(db, Row, [primary_key])


def update_rows(db: str, Row: type[BaseRow], primary_key2kwargs: Mapping[tuple | dict, Mapping[str, Any]]) -> None:
    """Update rows in a table in the database."""
    if len(primary_key2kwargs) == 0:
        return
    engine = sql.create_engine(db)
    inspector = sql.inspect(engine)
    if not inspector.has_table(Row.__tablename__):
        log("warning", f'No "{Row.__tablename__}" table found in the database.')
        return
    with sql.orm.sessionmaker(engine).begin() as session:
        for primary_key, kwargs in primary_key2kwargs.items():
            row = session.get(Row, primary_key)
            if row is None:
                log("warning", f'Row with primary key "{primary_key}" not present in "{Row.__tablename__}" table')
            else:
                for key, value in kwargs.items():
                    setattr(row, key, value)


def update_row(db: str, Row: type[BaseRow], primary_key: tuple | dict, **kwargs) -> None:
    """Update row in a table in the database."""
    update_rows(db, Row, {primary_key: kwargs})


def get_rows[T: BaseRow](db: str, Row: type[T], sql_stmt: Optional[str] = None) -> Sequence[T]:
    """Get (possibly filtered, ordered, grouped) rows of a table in the database."""
    engine = sql.create_engine(db)
    rows: Sequence[T] = []
    inspector = sql.inspect(engine)
    if not inspector.has_table(Row.__tablename__):
        log("warning", f'No "{Row.__tablename__}" table found in the database.')
        return rows
    with sql.orm.Session(engine) as session:
        stmt: Executable
        if sql_stmt is None:
            stmt = sql.select(Row)
        else:
            stmt = sql.text(sql_stmt)
        rows = session.scalars(stmt).all()
    return rows


def get_row[T: BaseRow](db: str, Row: type[T], primary_key: tuple | dict) -> T | None:
    """Get row of a table in the database based on the primary key."""
    engine = sql.create_engine(db)
    inspector = sql.inspect(engine)
    if not inspector.has_table(Row.__tablename__):
        log("warning", f'No "{Row.__tablename__}" table found in the database.')
        return None
    with sql.orm.Session(engine) as session:
        row = session.get(Row, primary_key)
    return row


def get_dataframe(db: str, Row: type[BaseRow], sql_stmt: Optional[str] = None) -> pd.DataFrame:
    """Get (possibly filtered, ordered, grouped) rows of a table in the database in a Pandas dataframe."""
    return pd.DataFrame([convert(row, dict) for row in get_rows(db, Row, sql_stmt)], columns=[attr.name for attr in sql.inspect(Row).columns])


def get_series(db: str, Row: type[BaseRow], primary_key: tuple | dict) -> pd.Series:
    """Get row of a table in the database based on the primary key in a Pandas Series."""
    row = get_row(db, Row, primary_key)
    return pd.Series(convert(row, dict) if row else None, index=[attr.name for attr in sql.inspect(Row).columns])
