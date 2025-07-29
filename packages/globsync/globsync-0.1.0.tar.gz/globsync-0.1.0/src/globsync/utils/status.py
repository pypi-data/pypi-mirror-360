"""Status utilities."""
import os.path
import shutil
import pandas as pd
import numpy as np
import math
from typing import Optional, Any
from bs4 import BeautifulSoup

from globsync import utils
import globsync.utils.db
import globsync.utils.paths
import globsync.utils.flows
import globsync.utils.users
import globsync.utils.email
from globsync.utils.paths import PathsRow
from globsync.utils.flows import FlowRunsRow
from globsync.utils.users import UsersRow
from globsync.utils.logging import log


def convert_size(size_bytes: int) -> str:
    """Get the a size in bytes to a human readable format."""
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"


def get_status(db: str, globus_secrets_file: Optional[str], sql_stmt: Optional[str]) -> pd.DataFrame:
    """Get the status of paths and flow runs."""
    paths = utils.db.get_dataframe(db, PathsRow, sql_stmt)
    flow_runs = utils.db.get_dataframe(db, FlowRunsRow)
    users = utils.db.get_dataframe(db, UsersRow)

    flows_client = utils.flows.get_flows_client(globus_secrets_file=globus_secrets_file)
    flow_runs["run_status"] = flow_runs.apply(lambda row: flows_client.get_run(row["run_id"])["status"] if pd.notna(row["run_id"]) else np.nan, axis=1)  # possible values run_status: "SUCCEEDED" "FAILED" "ENDED" "ACTIVE" "INACTIVE"

    status = pd.merge(pd.merge(paths, flow_runs, on="source_path", how="outer"), users, on="user", how="left")
    status["source_exists"] = status["source_path"].apply(lambda path: os.path.exists(path))

    return status


def autoclean(status: pd.DataFrame, db: Optional[str] = None) -> pd.DataFrame:
    """Automatically clean the paths and flow runs from the status and also the db if provided."""
    if db:
        utils.db.rm_rows(db, FlowRunsRow, status[status["run_status"].isin(["FAILED", "ENDED"])]["run_id"])
    status = status[~status["run_status"].isin(["FAILED", "ENDED"])]

    grouped = status.groupby("source_path")
    for path, group in grouped:
        if (group["run_status"] == "SUCCEEDED").all() and group["remove_source"].any() and group["source_exists"].iloc[0]:
            shutil.rmtree(path)
            status.loc[group.index, 'source_exists'] = False
    status_no_source = grouped.filter(lambda x: not x["source_exists"].iloc[0])
    if db:
        utils.db.rm_rows(db, PathsRow, status_no_source[pd.notna(status_no_source["user"])].groupby("source_path").head(1)["source_path"])
        utils.db.rm_rows(db, FlowRunsRow, status_no_source[pd.notna(status_no_source["run_id"])]["run_id"])
    status = grouped.filter(lambda x: x["source_exists"].iloc[0])

    if db:
        utils.db.rm_rows(db, FlowRunsRow, status[(status["run_status"] == "SUCCEEDED") & pd.isna(status["user"])]["run_id"])
    status = status[~((status["run_status"] == "SUCCEEDED") & pd.isna(status["user"]))]

    return status


def notify(status: pd.DataFrame, init_command: str, email_sender: str, email_backend: str, **kwargs) -> None:
    """Notify users of actions to be taken based on status."""
    status = autoclean(status)
    user_grouped = status.groupby("user")
    for user, group in user_grouped:
        if pd.isna(user):
            continue
        if pd.isna(group["email"].iloc[0]):
            log('warning', f"User {user} not registered within globsync.")
            continue
        group_backup = group[pd.isna(group["run_id"])]
        group_remove = group.groupby("source_path").filter(lambda x: (x["run_status"] == "SUCCEEDED").all()).groupby("source_path").head(1)

        data: dict[str, Any] = {}
        data["user_name"] = group["name"].iloc[0]
        data["cluster_name"] = (" " + os.getenv("VSC_INSTITUTE_CLUSTER", default="")) if os.getenv("VSC_INSTITUTE_CLUSTER", default="") else ""
        data["init_command"] = init_command
        data["source_paths_backup"] = [(source_path, convert_size(size)) for source_path, size in zip(group_backup["source_path"], group_backup["size"])]
        data["source_paths_remove"] = [(source_path, convert_size(size)) for source_path, size in zip(group_remove["source_path"], group_remove["size"])]
        subtype2body = {'html': utils.email.create_body('user_notification.html', data)}
        subtype2body['plain'] = BeautifulSoup(subtype2body['html'], "html.parser").get_text()
        subject = f'HPC storage usage notification'
        msg = utils.email.create_msg(email_sender, group["email"].iloc[0], subject, subtype2body)
        utils.email.send_msg(msg, email_backend, **kwargs)
