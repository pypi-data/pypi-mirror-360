"""Configuration utilities."""
import os
import os.path
import pathlib
import yaml

from globsync.utils.logging import log


def get_config_files() -> dict[str, str]:
    """Get the name of the YAML configuration file."""
    config_files: dict[str, str] = {}
    config_files['system'] = os.path.join("/etc/globsync.conf")
    # config_files['global'] = os.path.join(os.getenv("VSC_HOME") if os.getenv("VSC_HOME") is not None else os.path.expanduser("~"), ".config", "globsync", "config")
    config_files['user'] = os.path.join(os.getenv("VSC_HOME", default="") if os.getenv("VSC_HOME", default="") else os.path.expanduser("~"), ".config", "globsync", "config")
    config_files['env'] = os.getenv("GLOBSYNC_CONFIG_FILE", default="")
    config_files = {scope: os.path.normpath(os.path.abspath(config_file)) for scope, config_file in config_files.items() if config_file}
    return config_files


def read_config(config_files: dict[str, str]) -> dict:
    """Read configuration from file(s)."""
    config = {}
    for config_file in config_files.values():
        if config_file is not None and os.path.isfile(config_file):
            try:
                config.update(yaml.safe_load(pathlib.Path(config_file).read_text(encoding='utf-8')))
            except Exception as e:
                log("warning", f'Problem reading config file "{config_file}": {e}')
    return config


def write_config(config: dict, config_file: str) -> None:
    """Write configuration to file."""
    with open(config_file, 'w') as f:
        yaml.safe_dump(config, f, default_flow_style=False, indent=2, encoding="utf-8")


# def generate_config(config_file: str, **kwargs) -> None:
#     """Save configuration to the YAML configuration file."""
#     yaml_config = yaml.safe_dump(kwargs, default_flow_style=False, indent=2)
#     os.makedirs(os.path.dirname(config_file), exist_ok=True)
#     pathlib.Path(config_file).write_text(yaml_config, encoding="utf-8")
