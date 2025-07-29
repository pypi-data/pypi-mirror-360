"""Users utilities."""
import sqlalchemy as sql
import sqlalchemy.orm
from sqlalchemy.orm import Mapped

from globsync.utils.db import BaseRow


# PathsRow type and accompanying utilities


class UsersRow(BaseRow):
    """Class for rows of the table 'users' table."""

    __tablename__ = "users"
    user: Mapped[str] = sql.orm.mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str]


def create_users_row(user: str, name: str, email: str) -> UsersRow:
    """Create a UsersRow row."""
    return UsersRow(user=user, name=name, email=email)
