"""Python module to build a JSON representation of a directory structure for RichTreeCLI."""

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rich_tree_cli.main import RichTreeCLI


def build_json(cli: "RichTreeCLI", path: Path) -> dict:
    """Build a dictionary representation of the directory structure."""
    if path == cli.root:
        tree_data: dict[str, str] = build_tree_dict(cli, path)
        return {
            "metadata": {
                "total_dirs": cli.dir_count,
                "total_files": cli.file_count,
                "root_path": str(path),
            },
            "tree": tree_data,
        }
    return build_tree_dict(cli, path)


def build_tree_dict(cli: "RichTreeCLI", path: Path) -> dict:
    """Build a more compact tree representation."""
    result = {}

    for item in cli.get_items(path):
        if cli.ignore_handler.should_ignore(item):
            continue

        if item.is_dir():
            result[item.name + "/"] = build_tree_dict(cli, item)
        else:
            try:
                lines = len(item.read_text(encoding="utf-8").splitlines())
            except UnicodeDecodeError:
                lines = 0
            result[item.name] = {"size": item.stat().st_size, "lines": lines}

    return result
