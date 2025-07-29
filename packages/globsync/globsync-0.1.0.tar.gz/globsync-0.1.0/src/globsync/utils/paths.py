"""Database utilities."""
from pathlib import Path
import subprocess
import datetime
import sqlalchemy as sql
import sqlalchemy.orm
from sqlalchemy.orm import Mapped
from typing import Optional

from globsync.utils.db import BaseRow


# PathsRow type and accompanying utilities


class PathsRow(BaseRow):
    """Class for rows of the table 'paths' table."""

    __tablename__ = "paths"
    source_path: Mapped[str] = sql.orm.mapped_column(primary_key=True)
    user: Mapped[str]
    size: Mapped[int]
    time_modified: Mapped[str]
    time_added: Mapped[str]


def create_paths_row(source_path: str, user: Optional[str] = None, size: Optional[int] = None, mtime: Optional[str] = None) -> PathsRow:
    """Create a PathsRow row for a given directory or file path."""
    if not user:
        user = Path(source_path).owner()
    if not size or not mtime:
        du_result = subprocess.run(['du', '-B1', '-s', '--time', '--time-style=full-iso', source_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        du_result.check_returncode()
        du_results = du_result.stdout.split('\t')
        size = int(du_results[0])
        time_modified = datetime.datetime.fromisoformat(du_results[1]).isoformat()
    else:
        time_modified = datetime.datetime.fromisoformat(mtime).isoformat()
    time_added = datetime.datetime.now(datetime.timezone.utc).astimezone().isoformat()
    return PathsRow(source_path=source_path, user=user, size=size, time_modified=time_modified, time_added=time_added)
