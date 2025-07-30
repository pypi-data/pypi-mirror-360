# IMPORTANT
# After changing this file, run `python3 -m lookout_config.generate_schemas`
# To re-generate the json schemas
import yaml
import os
from typing import Any
from pathlib import Path

from lookout_config.types import (
    LookoutConfig,
    Mode,
    LogLevel,
    Network,
    GeolocationMode,
    Point,
    Polygon,
    Camera,
    PositioningSystem,
)
from lookout_config.helpers import YamlDumper


LOOKOUT_CONFIG_FILE_NAME = "lookout.yml"
LOOKOUT_SCHEMA_URL = "https://greenroom-robotics.github.io/lookout/schemas/lookout.schema.json"


def find_config() -> Path:
    """Returns the path to the .config/greenroom directory"""
    return Path.home().joinpath(".config/greenroom")


def get_path():
    return find_config() / LOOKOUT_CONFIG_FILE_NAME


def parse(config: dict[str, Any]) -> LookoutConfig:
    return LookoutConfig(**config or {})


def read() -> LookoutConfig:
    path = get_path()
    with open(path) as stream:
        return parse(yaml.safe_load(stream))


def write(config: LookoutConfig):
    path = get_path()
    # Make the parent dir if it doesn't exist
    os.makedirs(path.parent, exist_ok=True)
    json_string = config.model_dump(mode="json")
    with open(path, "w") as stream:
        print(f"Writing: {path}")
        headers = f"# yaml-language-server: $schema={LOOKOUT_SCHEMA_URL}"
        data = "\n".join([headers, yaml.dump(json_string, Dumper=YamlDumper, sort_keys=True)])
        stream.write(data)


__all__ = [
    "find_config",
    "get_path",
    "parse",
    "read",
    "write",
    "LOOKOUT_SCHEMA_URL",
    "LookoutConfig",
    "Mode",
    "LogLevel",
    "Network",
    "GeolocationMode",
    "Point",
    "Polygon",
    "Camera",
    "PositioningSystem",
]
