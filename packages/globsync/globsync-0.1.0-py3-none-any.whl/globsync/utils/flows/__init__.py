"""Globus utilities."""
import os
import os.path
import datetime
import sqlalchemy as sql
import sqlalchemy.orm
from sqlalchemy.orm import Mapped
from globus_sdk import AuthLoginClient, NativeAppAuthClient, ConfidentialAppAuthClient, AccessTokenAuthorizer, ClientCredentialsAuthorizer, FlowsClient, SpecificFlowClient
from globus_sdk.authorizers import GlobusAuthorizer
from globus_sdk.scopes import Scope, SpecificFlowScopeBuilder, TransferScopes, GCSCollectionScopeBuilder
from globus_sdk.scopes.data import FlowsScopes
from globus_sdk.login_flows import CommandLineLoginFlowManager
from globus_sdk.gare import GlobusAuthorizationParameters
import json
import yaml
from typing import Optional, Any
from collections.abc import Callable

from globsync import utils
import globsync.utils.db
from globsync.utils.db import BaseRow
from globsync.utils.logging import log


def abspath(path: str, path_prefix: str) -> str:
    """Construct absolute path for possibly relative path."""
    if os.path.isabs(path):
        return os.path.normpath(path)
    return os.path.normpath(os.path.join(path_prefix, path))


sync_level2name = ['exists', 'size', 'mtime', 'checksum']
sync_name2level = {name: level for level, name in enumerate(sync_level2name)}


class FlowRunsRow(BaseRow):
    """Class for rows of the table 'flow_runs' table."""

    __tablename__ = "flow_runs"
    run_id: Mapped[str] = sql.orm.mapped_column(primary_key=True)
    flow_id: Mapped[str]
    source_path: Mapped[str]
    source_path_endpoint: Mapped[str]
    destination_path: Mapped[str]
    source_endpoint: Mapped[str]
    destination_endpoint: Mapped[str]
    recursive: Mapped[bool]
    filter_rules: Mapped[str]
    sync_level: Mapped[str]
    verify_checksum: Mapped[bool]
    preserve_timestamp: Mapped[bool]
    encrypt_data: Mapped[bool]
    remove_source: Mapped[bool]
    remove_destination: Mapped[bool]
    time_started: Mapped[str]


def create_flow_runs_row(run_id: str, flow_id: str, source_path: str, source_path_endpoint: str, destination_path: str, source_endpoint: str, destination_endpoint: str, recursive: bool, filter_rules: str, sync_level: str, verify_checksum: bool, preserve_timestamp: bool, encrypt_data: bool, remove_source: bool, remove_destination: bool) -> FlowRunsRow:
    """Construct a flow input object from a FlowRunsRow object."""
    row = FlowRunsRow()
    row.run_id = run_id
    row.flow_id = flow_id
    row.source_path = source_path
    row.source_path_endpoint = source_path_endpoint
    row.destination_path = destination_path
    row.source_endpoint = source_endpoint
    row.destination_endpoint = destination_endpoint
    row.recursive = recursive
    row.filter_rules = filter_rules
    row.sync_level = sync_level
    row.verify_checksum = verify_checksum
    row.preserve_timestamp = preserve_timestamp
    row.encrypt_data = encrypt_data
    row.remove_source = remove_source
    row.remove_destination = remove_destination
    row.time_started = datetime.datetime.now(datetime.timezone.utc).astimezone().isoformat()
    return row


def read_secrets(globus_secrets_file: str) -> dict:
    """Read the Globus secrets from disk."""
    with open(globus_secrets_file, 'r') as f:
        secrets = yaml.safe_load(f)
    return secrets


def read_flow_definition(flow_definition_file: str) -> dict:
    """Read the Globus flow definition from disk."""
    with open(flow_definition_file, 'r') as f:
        definition = json.load(f)
    return definition


def read_flow_input_schema(flow_input_schema_file: str) -> dict:
    """Read the Globus flow input schema from disk."""
    with open(flow_input_schema_file, 'r') as f:
        input_schema = json.load(f)
    return input_schema


def construct_flow_input(row: FlowRunsRow) -> dict[str, Any]:
    """Construct a flow input object from a FlowRunsRow object."""
    flow_input: dict[str, Any] = {}
    flow_input["source"] = {"id": row.source_endpoint, "path": row.source_path_endpoint}
    flow_input["destination"] = {"id": row.destination_endpoint, "path": row.destination_path}
    flow_input["sync_level"] = sync_name2level[row.sync_level]
    flow_input["remove_source"] = row.remove_source
    flow_input["remove_destination"] = row.remove_destination
    flow_input["encrypt_data"] = row.encrypt_data
    flow_input["verify_checksum"] = row.verify_checksum
    flow_input["preserve_timestamp"] = row.preserve_timestamp
    flow_input["recursive"] = row.recursive
    flow_input["filter_rules"] = []
    for filter_rule in row.filter_rules.split(","):
        filter_rule = filter_rule.strip()
        if not filter_rule:
            continue
        if filter_rule[0] == "+":
            filter_rule = filter_rule[1:].strip()
            flow_input["filter_rules"].append({"method": "include", "name": filter_rule})
        elif filter_rule[0] == "-":
            filter_rule = filter_rule[1:].strip()
            flow_input["filter_rules"].append({"method": "exclude", "name": filter_rule})
        else:
            log("warning", f'Filter rule "{filter_rule}" is not valid.')
    return flow_input


def get_flows_scope() -> Scope:
    """Create Scope object for use in the FlowsClient."""
    return Scope(FlowsScopes.all)


def get_flow_scope(flow_id: str, source_endpoint: str, destination_endpoint: str) -> Scope:
    """Create Scope object for use in the SpecificFlowsClient."""
    flow_scope = Scope(SpecificFlowScopeBuilder(flow_id).user)
    transfer_scope = Scope(TransferScopes.all)
    flow_scope.add_dependency(transfer_scope)
    transfer_scope.add_dependency(GCSCollectionScopeBuilder(source_endpoint).data_access)
    transfer_scope.add_dependency(GCSCollectionScopeBuilder(destination_endpoint).data_access)
    return flow_scope


def get_authorizer(required_scopes: list[Scope], globus_secrets_file: Optional[str] = None) -> GlobusAuthorizer:
    """Get a Globus Authorizer."""
    auth_client: AuthLoginClient
    authorizer: GlobusAuthorizer
    if globus_secrets_file and os.access(globus_secrets_file, os.R_OK):
        secrets = read_secrets(globus_secrets_file)
        auth_client = ConfidentialAppAuthClient(client_id=secrets["CLIENT_ID"], client_secret=secrets["CLIENT_SECRET"])
        authorizer = ClientCredentialsAuthorizer(auth_client, [str(scope) for scope in required_scopes])
    else:
        auth_client = NativeAppAuthClient(client_id="a48e73cd-39c0-4cb2-b0d8-0288d343dd45")
        login_manager = CommandLineLoginFlowManager(auth_client)
        token_response = login_manager.run_login_flow(GlobusAuthorizationParameters(required_scopes=[str(scope) for scope in required_scopes]))
        authorizer = AccessTokenAuthorizer(next(iter(token_response.by_resource_server.values()))['access_token'])
    return authorizer


def get_flows_client(globus_secrets_file: Optional[str] = None) -> FlowsClient:
    """Get a FlowsClient."""
    scope = get_flows_scope()
    authorizer = get_authorizer([scope], globus_secrets_file)
    return FlowsClient(authorizer=authorizer)


def get_flow_client(flow_id: str, source_endpoint: str, destination_endpoint: str, globus_secrets_file: Optional[str] = None) -> SpecificFlowClient:
    """Get a SpecificFlowClient."""
    scope = get_flow_scope(flow_id, source_endpoint, destination_endpoint)
    authorizer = get_authorizer([scope], globus_secrets_file)
    return SpecificFlowClient(flow_id, authorizer=authorizer)


def config_flow(flow_id: str, flow_definition_file: str, flow_input_schema_file: str, globus_secrets_file: Optional[str]) -> None:
    """Update Globus flow."""
    flow_definition = read_flow_definition(flow_definition_file)
    flow_input_schema = read_flow_input_schema(flow_input_schema_file)
    flows_client = get_flows_client(globus_secrets_file)
    flows_client.update_flow(flow_id, definition=flow_definition, input_schema=flow_input_schema)


def start_flow_run(db: str, source_endpoint: str, destination_endpoint: str, source_path_prefix: str, source_path_prefix_endpoint: Optional[str], destination_path_prefix: Optional[str], recursive: bool, filter_rules: str, sync_level: str, verify_checksum: bool, preserve_timestamp: bool, encrypt_data: bool, remove_source: bool, remove_destination: bool, source_path: str, destination_path: Optional[str], flow_id: str) -> None:
    """Start a Globus flow run."""
    source_path_prefix = os.path.normpath(source_path_prefix)
    source_path = os.path.abspath(source_path)
    if source_path[:len(source_path_prefix)] != source_path_prefix:
        log("warning", f'The source path "{source_path}" is not a descendant of the source_path_prefix {source_path_prefix}.')
        return
    if source_path_prefix_endpoint:
        source_path_endpoint = source_path_prefix_endpoint + source_path[len(source_path_prefix):]
    else:
        source_path_endpoint = source_path
    destination_path = abspath(destination_path if destination_path else os.path.relpath(source_path, start=source_path_prefix), destination_path_prefix if destination_path_prefix else source_path_prefix)

    flow_client = get_flow_client(flow_id, source_endpoint, destination_endpoint)
    row = create_flow_runs_row("", flow_id, source_path, source_path_endpoint, destination_path, source_endpoint, destination_endpoint, recursive, filter_rules, sync_level, verify_checksum, preserve_timestamp, encrypt_data, remove_source, remove_destination)
    flow_input = construct_flow_input(row)
    flow = flow_client.run_flow(flow_input, label=f"Transfer of << {os.path.basename(source_path)} >>", run_managers=["urn:globus:auth:identity:a48e73cd-39c0-4cb2-b0d8-0288d343dd45", "urn:globus:auth:identity:acaa42a0-f944-4cd3-b79c-e66be024bba7", "urn:globus:auth:identity:207658db-ddf7-4fe5-9861-c1013ccbbb57"])
    row.run_id = flow["run_id"]
    utils.db.add_row(db, row)


def cancel_flow_run(run_id: str, globus_secrets_file: Optional[str]) -> None:
    """Cancel a Globus flow run."""
    flows_client = get_flows_client(globus_secrets_file=globus_secrets_file)
    flows_client.cancel_run(run_id)
