"""Python module to convert JSON data to TOML format for RichTreeCLI."""

import tomli_w as toml


def _ensure_tables(json_data: dict) -> dict:
    """Return a dictionary with explicit metadata and tree tables."""
    return {
        "metadata": json_data.get("metadata", {}),
        "tree": json_data.get("tree", json_data),
    }


def build_toml(json_data: dict) -> str:
    """Convert JSON data to TOML format with explicit tables.

    The returned TOML mirrors the JSON structure using ``[metadata]`` and
    ``[tree]`` tables.

    Args:
        json_data (dict): The JSON data to convert.
    """
    toml_data = _ensure_tables(json_data)
    return toml.dumps(toml_data)
