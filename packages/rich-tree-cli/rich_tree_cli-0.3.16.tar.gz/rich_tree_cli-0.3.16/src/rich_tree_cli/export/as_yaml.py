"""Python module to convert JSON data to YAML format for RichTreeCLI."""

import yaml


def build_yaml(json_data: dict) -> str:
    """Convert JSON data to YAML format."""
    return yaml.safe_dump(json_data, sort_keys=False)
