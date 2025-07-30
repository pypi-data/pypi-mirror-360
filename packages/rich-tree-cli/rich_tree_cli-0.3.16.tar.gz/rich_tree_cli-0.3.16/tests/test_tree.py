from operator import neg
from pathlib import Path, PureWindowsPath

from rich_tree_cli import RichTreeCLI
from rich_tree_cli.export.icons import GlyphsIcons as TerminalIcons
from rich_tree_cli.ignore_handler import IgnoreHandler


def test_get_file_string_metadata_all(tmp_path: Path):
    term = TerminalIcons()
    sample = tmp_path / "sample.txt"
    sample.write_text("hello\nworld\n")
    cli = RichTreeCLI(directory=tmp_path, metadata="all", icons="glyphs")
    result = cli.get_file_string(sample)
    assert f"{term.get_icon('FILE')} {sample.name}" in result
    assert str(sample.stat().st_size) in result
    assert "2 lines" in result


def test_add_to_tree_counts(tmp_path: Path):
    term = TerminalIcons()
    folder = tmp_path / "folder"
    folder.mkdir()
    (folder / "inner.txt").write_text("data")
    (tmp_path / "root.txt").write_text("root")
    cli = RichTreeCLI(directory=tmp_path, icons="glyphs")
    cli.add_to_tree(tmp_path, cli.tree)
    assert cli.dir_count == 1
    assert cli.file_count == 2
    labels = [child.label for child in cli.tree.children]
    assert f"{term.get_icon('FOLDER')} folder" in labels
    assert f"{term.get_icon('FILE')} root.txt" in labels


def test_ignore_handler_windows_paths(tmp_path: Path) -> None:
    """Ensure Windows-style paths are correctly handled on any platform."""
    handler = RichTreeCLI(directory=tmp_path).ignore_handler

    dist_dir = tmp_path / "dist"
    dist_dir.mkdir()
    dist_win = str(PureWindowsPath(dist_dir.as_posix()))
    assert handler.should_ignore(dist_win) is True

    lock_file = tmp_path / "file.lock"
    lock_file.write_text("lock")
    lock_win = str(PureWindowsPath(lock_file.as_posix()))
    assert handler.should_ignore(lock_win) is True

    other_file = tmp_path / "keep.txt"
    other_file.write_text("keep")
    other_win = str(PureWindowsPath(other_file.as_posix()))
    assert handler.should_ignore(other_win) is False


def test_should_ignore(tmp_path: Path):
    ignore_handler = IgnoreHandler()
    ignored_file = tmp_path / "__pycache__"
    ignored_file.mkdir()
    non_ignored_file = tmp_path / "test.txt"
    non_ignored_file.write_text("test")

    assert ignore_handler.should_ignore(ignored_file) is True
    assert ignore_handler.should_ignore(non_ignored_file) is False
    assert ignore_handler.should_ignore(str(non_ignored_file)) is False
    assert ignore_handler.should_ignore(str(ignored_file)) is True

    if non_ignored_file.exists():
        non_ignored_file.unlink()
    if ignored_file.exists():
        ignored_file.rmdir()


def test_max_depth_positive(tmp_path: Path):
    cli = RichTreeCLI(directory=tmp_path, max_depth=neg(1))
    assert cli.max_depth >= 0, "max_depth should be greater than zero"
