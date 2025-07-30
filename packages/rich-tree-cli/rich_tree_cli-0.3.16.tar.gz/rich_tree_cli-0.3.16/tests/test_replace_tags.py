from pathlib import Path

from rich_tree_cli import OutputManager, RichTreeCLI


def test_replace_tags(tmp_path: Path) -> None:
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "file.txt").write_text("content")

    readme = tmp_path / "README.md"
    readme.write_text("before\n<replace_me></replace_me>\nafter\n", encoding="utf-8")

    cli = RichTreeCLI(
        directory=tmp_path,
        replace_path=readme,
        replace_tag="<replace_me></replace_me>",
        disable_color=True,
        no_console=True,
    )
    manager = OutputManager(disable_color=True)
    manager.set_cli(cli)
    result = cli.run()
    manager.output(result, ["text"], None)

    updated = readme.read_text(encoding="utf-8")
    assert "file.txt" in updated
    assert updated.count("<replace_me>") == 1
    assert updated.count("</replace_me>") == 1
