"""CLI utilities."""
import os
import os.path
import click
from typing import Any, Optional
from collections.abc import Callable
import yaml

from globsync import utils
import globsync.utils.config
import globsync.utils.db
import globsync.utils.paths
import globsync.utils.users
import globsync.utils.flows
import globsync.utils.status
import globsync.utils.logging
from globsync.utils.paths import PathsRow
from globsync.utils.users import UsersRow
from globsync.utils.flows import FlowRunsRow
from globsync.utils.logging import log


def opt_default(keys: str | list, default: Optional[Any] = None, default_map: Optional[Callable] = None) -> Any:
    """Get the default setting for an option based on the default map."""
    if isinstance(keys, str):
        keys = [key for key in keys.split("/") if len(key)]
    assert len(keys)
    if default_map is None:
        def default_map():
            return click.get_current_context().find_root().default_map
    if len(keys) > 1:
        return opt_default(keys[1:], default, lambda: default_map().get(keys[0], {}))
    return lambda: default_map().get(keys[0], default)


auto_envvar_prefix = "GLOBSYNC"


# Logging options
opt_log_file = click.option("--log-file", type=str, help="The log file", envvar=auto_envvar_prefix + "_LOG_FILE", default=opt_default("log_file"))
opt_verbosity = click.option('--verbosity', type=click.Choice(list(utils.logging.level_str2int.keys())), help="Verbosity level", envvar=auto_envvar_prefix + "_VERBOSITY", default=opt_default("verbosity", "info"))


# Common options and arguments
opt_db = click.option("-d", "--db", "--database", type=str, required=True, help="The database URL", envvar=auto_envvar_prefix + "_DB", default=opt_default("db"))

# Paths options and arguments
opt_user = click.option("--user", type=str, help="The user responsible for the path")
opt_size = click.option("--size", type=int, help="The disk usage size in bytes")
opt_mtime = click.option("--mtime", type=str, help="The time of last data modification in some ISO 8601 format")
arg_source_path = click.argument("source-path", type=str, required=True)
arg_destination_path = click.argument("destination-path", type=str, required=False)

opt_sql_stmt = click.option("--sql_stmt", type=str, help="The user name", envvar="_SQL_STMT")  # , default=opt_default("sql_stmt", "SELECT * FROM paths ORDER BY size"))

# Users options and arguments
arg_user = click.argument("user", type=str, required=True)
arg_name = click.argument("name", type=str, required=True)
arg_email = click.argument("email", type=str, required=True)

# Transfer options and arguments
opt_source_endpoint = click.option("--source-endpoint", type=str, required=True, help="The source endpoint UUID", envvar=auto_envvar_prefix + "_SOURCE_ENDPOINT", default=opt_default("source_endpoint"))
opt_destination_endpoint = click.option("--destination-endpoint", type=str, required=True, help="The destination endpoint UUID", envvar=auto_envvar_prefix + "_DESTINATION_ENDPOINT", default=opt_default("destination_endpoint"))
opt_source_path_prefix = click.option("--source-path-prefix", type=str, help="The source path prefix", envvar=auto_envvar_prefix + "_SOURCE_PATH_PREFIX", default=opt_default("source_path_prefix", os.getcwd()))
opt_source_path_prefix_endpoint = click.option("--source-path-prefix-endpoint", type=str, help="The source path prefix on the source endpoint", envvar=auto_envvar_prefix + "_SOURCE_PATH_PREFIX_ENDPOINT", default=opt_default("source_path_prefix_endpoint"))
opt_destination_path_prefix = click.option("--destination-path-prefix", type=str, required=False, help="The destination path prefix", envvar=auto_envvar_prefix + "_DESTINATION_PATH_PREFIX", default=opt_default("destination_path_prefix"))
opt_recursive = click.option('--recursive/--no-recursive', help="Recurse into directories", envvar=auto_envvar_prefix + "_RECURSIVE", default=opt_default("recursive", True))
opt_filter_rules = click.option("--filter-rules", type=str, required=False, help="Comma-separated list of include (+) and exclude (-) filter rules to be applied in given order, e.g.: + *.tgz, - *.tar.gz", envvar=auto_envvar_prefix + "_FILTER_RULES", default=opt_default("filter_rules", ''))
opt_sync_level = click.option('--sync-level', type=click.Choice(['exists', 'size', 'mtime', 'checksum']), help="Synchronization level", envvar=auto_envvar_prefix + "_SYNC_LEVEL", default=opt_default("sync_level", "checksum"))
opt_verify_checksum = click.option('--verify-checksum/--no-verify-checksum', help="Verify checksum", envvar=auto_envvar_prefix + "_VERIFY_CHECKSUM", default=opt_default("verify_checksum", True))
opt_preserve_timestamp = click.option('--preserve-timestamp/--no-preserve-timestamp', help="Preserve timestamps", envvar=auto_envvar_prefix + "_PRESERVE_TIMESTAMP", default=opt_default("preserve_timestamp", True))
opt_encrypt_data = click.option('--encrypt-data/--no-encrypt-data', help="Encrypt data during transfer", envvar=auto_envvar_prefix + "_ENCRYPT_DATA", default=opt_default("encrypt_data", False))
opt_remove_source = click.option('--remove-source/--no-remove-source', help="Remove source path after transfer succeeds", envvar=auto_envvar_prefix + "_REMOVE_SOURCE", default=opt_default("remove_source", False))
opt_remove_destination = click.option('--remove-destination/--no-remove-destination', help="Remove destination files and directories not available on the source path", envvar=auto_envvar_prefix + "_REMOVE_DESTINATION", default=opt_default("remove_destination", False))

# Flows options and arguments
opt_flow_id = click.option("--flow-id", type=str, help="The Globus flow id", envvar=auto_envvar_prefix + "_FLOW_ID", default=opt_default("flow_id", "6da700cd-c491-43f0-924d-501ee1f3ed3d"))
arg_run_id = click.argument("run-id", type=str, required=True)
opt_globus_secrets_file = click.option("--globus-secrets-file", type=str, help="The Globus secrets file", envvar=auto_envvar_prefix + "_GLOBUS_SECRETS_FILE", default=opt_default("globus_secrets_file"))
opt_flow_definition_file = click.option("--flow-definition-file", type=str, help="The flow definition file", envvar=auto_envvar_prefix + "_FLOW_DEFINITION_FILE", default=opt_default("flow_definition_file", os.path.join(os.path.dirname(__file__), "utils/flows/definitions/transfer.json")))
opt_flow_input_schema_file = click.option("--flow-input-schema-file", type=str, help="The flow input schema file", envvar=auto_envvar_prefix + "_FLOW_INPUT_SCHEMA_FILE", default=opt_default("flow_input_schema_file", os.path.join(os.path.dirname(__file__), "utils/flows/input-schemas/transfer.json")))

# Status options and arguments
opt_init_command = click.option("--init-command", type=str, required=True, help="The initialization command", envvar=auto_envvar_prefix + "_INIT_COMMAND", default=opt_default("init_command"))
opt_email_sender = click.option("--email-sender", type=str, required=True, help="The administrator's email", envvar=auto_envvar_prefix + "_EMAIL_SENDER", default=opt_default("email_sender"))
opt_email_backend = click.option("--email-backend", type=click.Choice(['smtp', 'linux_mail', 'gmail', 'office365']), help="The backend used for sending emails", envvar=auto_envvar_prefix + "_EMAIL_BACKEND", default=opt_default("email_backend", 'smtp'))
opt_gmail_secrets_file = click.option("--gmail-secrets-file", type=str, help="The Gmail secrets file", envvar=auto_envvar_prefix + "_GMAIL_SECRETS_FILE", default=opt_default("gmail_secrets_file"))

def entry_callback(ctx, param, value):
    if value:
        log('debug', f'entry: {ctx.command_path} {ctx.params}')
    return value


def exit_callback_callback(ctx, param, value):
    if value:
        def exit_callback():
            log('debug', f'exit: {ctx.command_path}')
        ctx.call_on_close(exit_callback)
    return value


opt_log_entry = click.option('--log-entry/--no-log-entry', default=True, callback=entry_callback, expose_value=False, hidden=True, is_eager=False)
opt_log_exit = click.option('--log-exit/--no-log-exit', default=True, callback=exit_callback_callback, expose_value=False, hidden=True, is_eager=False)



@click.group()
@opt_log_file
@opt_verbosity
def main(log_file: Optional[str], verbosity: str) -> None:
    """globsync CLI."""
    if log_file:
        utils.logging.init_file_handler(log_file)
    utils.logging.handlers["stdout"].setLevel(utils.logging.level_str2int[verbosity.lower()])


@main.group('config')
def main_config() -> None:
    """Configuration commands."""
    pass


@main_config.command('show')
@opt_log_entry
@opt_log_exit
def main_config_show() -> None:
    """Show settings as defined by the configuration files."""
    log('debug', 'main_config_show.')
    log("info", yaml.safe_dump(click.get_current_context().find_root().default_map, default_flow_style=False, indent=2))


@main_config.command('files')
@opt_log_entry
@opt_log_exit
def main_config_files() -> None:
    """List configuration files globsync would read in case they are available."""
    log("info", str(utils.config.get_config_files()))


@main_config.command('flow')
@opt_log_entry
@opt_log_exit
@opt_flow_id
@opt_flow_definition_file
@opt_flow_input_schema_file
@opt_globus_secrets_file
def main_config_flow(**kwargs) -> None:
    """Configure the flow definition and input schema."""
    utils.flows.config_flow(**kwargs)


@main.group('paths')
def main_paths() -> None:
    """Path commands."""
    pass


@main_paths.command('add')
@opt_log_entry
@opt_log_exit
@opt_db
@opt_user
@opt_size
@opt_mtime
@arg_source_path
def main_paths_add(db: str, user: Optional[str], size: Optional[int], mtime: Optional[str], source_path: str) -> None:
    """Add (absolute or relative) PATH to the paths list."""
    if os.path.exists(source_path):
        utils.db.add_row(db, utils.paths.create_paths_row(os.path.abspath(source_path), user, size, mtime))
    else:
        log('warning', f'Path "{source_path}" does not exist.')


@main_paths.command('rm')
@opt_log_entry
@opt_log_exit
@opt_db
@arg_source_path
def main_paths_rm(db: str, source_path: str) -> None:
    """Remove (absolute or relative) PATH from the paths list."""
    utils.db.rm_row(db, PathsRow, (os.path.abspath(source_path),))


@main_paths.command('list')
@opt_log_entry
@opt_log_exit
@opt_db
@opt_sql_stmt
def main_paths_list(db: str, sql_stmt: Optional[str]) -> None:
    """List the paths."""
    paths = utils.db.get_dataframe(db, PathsRow, sql_stmt)
    if len(paths):
        log("info", paths.to_string(index=False))
    # where_args = tuple((getattr(PathsRow, key) == val) for key, val in kwargs.items() if val is not None)
    # order_args = (sql.desc(PathsRow.size),)


@main.group('users')
def main_users() -> None:
    """User commands."""
    pass


@main_users.command('add')
@opt_log_entry
@opt_log_exit
@opt_db
@arg_user
@arg_name
@arg_email
def main_users_add(db: str, user: str, name: str, email: str) -> None:
    """Add user to the users list."""
    utils.db.add_row(db, utils.users.create_users_row(user, name, email))


@main_users.command('rm')
@opt_log_entry
@opt_log_exit
@opt_db
@arg_user
def main_users_rm(db: str, user: str) -> None:
    """Remove user from the users list."""
    utils.db.rm_row(db, UsersRow, (user,))


@main_users.command('list')
@opt_log_entry
@opt_log_exit
@opt_db
@opt_sql_stmt
def main_users_list(db: str, sql_stmt: Optional[str]) -> None:
    """List the users."""
    users = utils.db.get_dataframe(db, UsersRow, sql_stmt)
    if len(users):
        log('info', users.to_string(index=False))


@main.group('flows')
def main_flows() -> None:
    """Globus flow commands."""
    pass


@main_flows.command('start')
@opt_log_entry
@opt_log_exit
@opt_db
@opt_source_endpoint
@opt_destination_endpoint
@opt_source_path_prefix
@opt_source_path_prefix_endpoint
@opt_destination_path_prefix
@opt_recursive
@opt_filter_rules
@opt_sync_level
@opt_verify_checksum
@opt_preserve_timestamp
@opt_encrypt_data
@opt_remove_source
@opt_remove_destination
@opt_flow_id
@arg_source_path
@arg_destination_path
def main_flows_start(**kwargs) -> None:
    """Start a Globus flow run."""
    utils.flows.start_flow_run(**kwargs)


@main_flows.command('cancel')
@opt_log_entry
@opt_log_exit
@opt_globus_secrets_file
@arg_run_id
def main_flows_cancel(**kwargs) -> None:
    """Cancel a Globus flow run."""
    utils.flows.cancel_flow_run(**kwargs)


@main_flows.command('rm')
@opt_log_entry
@opt_log_exit
@opt_db
@arg_run_id
def main_flows_rm(db: str, run_id: str) -> None:
    """Remove a Globus flow run from the list."""
    utils.db.rm_row(db, FlowRunsRow, (run_id,))


@main_flows.command('list')
@opt_log_entry
@opt_log_exit
@opt_db
@opt_sql_stmt
def main_flows_list(db: str, sql_stmt: Optional[str]) -> None:
    """List the flow runs."""
    flow_runs = utils.db.get_dataframe(db, FlowRunsRow, sql_stmt)
    if len(flow_runs):
        log("info", flow_runs.to_string(index=False))


@main.group('status')
def main_status() -> None:
    """Status commands."""
    pass


@main_status.command('show')
@opt_log_entry
@opt_log_exit
@opt_db
@opt_globus_secrets_file
@opt_sql_stmt
def main_status_show(db: str, globus_secrets_file: Optional[str], sql_stmt: Optional[str]) -> None:
    """Show the status of paths and flow runs."""
    status = utils.status.get_status(db, globus_secrets_file, sql_stmt)
    if len(status):
        status = status[["source_path", "source_exists", "user", "name", "size", "run_id", "remove_source", "time_started", "run_status"]]
        log("info", status.to_string(index=False))


@main_status.command('autoclean')
@opt_log_entry
@opt_log_exit
@opt_db
@opt_globus_secrets_file
@opt_sql_stmt
def main_status_autoclean(db: str, globus_secrets_file: Optional[str], sql_stmt: Optional[str]) -> None:
    """Automatically clean the paths and flow runs based on status."""
    utils.status.autoclean(utils.status.get_status(db, globus_secrets_file, sql_stmt), db)


@main_status.command('notify')
@opt_log_entry
@opt_log_exit
@opt_db
@opt_globus_secrets_file
@opt_sql_stmt
@opt_init_command
@opt_email_sender
@opt_email_backend
@opt_gmail_secrets_file
def main_status_notify(db: str, globus_secrets_file: Optional[str], sql_stmt: Optional[str], init_command: str, email_sender: str, email_backend: str, gmail_secrets_file: Optional[str]) -> None:
    """Notify users of actions to be taken based on status."""
    utils.status.notify(utils.status.get_status(db, globus_secrets_file, sql_stmt), init_command, email_sender, email_backend, gmail_secrets_file=gmail_secrets_file)


def entry_point() -> None:
    """Entry point to the CLI."""
    default_map = utils.config.read_config(utils.config.get_config_files())
    main(obj={}, default_map=default_map)  # , auto_envvar_prefix=auto_envvar_prefix
