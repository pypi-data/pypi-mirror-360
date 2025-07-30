"""Helpers for replacing tag blocks with tree output."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rich_tree_cli.main import RichTreeCLI
    from rich_tree_cli.output_manager import OutputManager


def _parse_tag_pair(tag: str) -> tuple[str, str]:
    """Return the opening and closing tags for ``tag``.

    The provided ``tag`` may be a simple tag name (``replace_me``), an HTML
    comment block (``<!-- rTree -->``), or a full pair like
    ``<replace_me></replace_me>``.
    """
    if tag.startswith("<!--") and tag.endswith("-->"):
        inner = tag[4:-3].strip()
        return tag, f"<!-- /{inner} -->"
    if tag.startswith("<") and tag.endswith(">") and "></" in tag:
        start, end = tag.split("></", 1)
        return start + ">", "</" + end
    if tag.startswith("<") and tag.endswith(">"):
        name = tag[1:-1]
        return tag, f"</{name}>"
    name = tag.strip()
    return f"<{name}>", f"</{name}>"


def output_to_file(output_manager: OutputManager, cli: RichTreeCLI) -> None:
    """Replace tagged block in ``cli.replace_path`` with tree output."""
    replace_path = cli.replace_path
    tag = cli.replace_tag or "<!-- rTree -->"

    if not replace_path or not replace_path.exists():
        output_manager.error(f"Error: The specified replace path '{replace_path}' does not exist.")
        return

    if replace_path.suffix in {".md", ".html"}:
        markdown_content = replace_path.read_text(encoding="utf-8")
        new_structure = output_manager.generate_output("markdown", cli.totals)
        updated_content = update_directory_structure(markdown_content, new_structure, tag)
        replace_path.write_text(updated_content, encoding="utf-8")
        output_manager.info(f"Content replaced successfully in {replace_path}.")


def update_directory_structure(markdown_content: str, new_structure: str, tag: str) -> str:
    """Inject ``new_structure`` between ``tag`` boundaries in ``markdown_content``."""
    start_tag, end_tag = _parse_tag_pair(tag)

    start = markdown_content.find(start_tag)
    end = markdown_content.find(end_tag)

    if start != -1 and end != -1:
        before = markdown_content[: start + len(start_tag)]
        after = markdown_content[end:]
        return f"{before}\n\n{new_structure}\n\n{after}"

    return markdown_content
