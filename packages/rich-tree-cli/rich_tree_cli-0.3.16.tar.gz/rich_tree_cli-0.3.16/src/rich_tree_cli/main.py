"""Rich Tree CLI: A command-line interface for displaying directory trees in a rich format."""

from argparse import ArgumentParser, Namespace
from importlib.metadata import version
from pathlib import Path
import sys
from typing import TYPE_CHECKING

from rich.tree import Tree

from ._get_console import get_console
from .constants import OutputFormat
from .export.icons import IconManager, IconMode
from .ignore_handler import IgnoreHandler
from .output_manager import OutputManager, RunResult

__version__: str = version("rich-tree-cli")

if TYPE_CHECKING:
    from rich.console import Console


class RichTreeCLI:
    """RichTreeCLI class to build and display a directory tree with various options."""

    def __init__(
        self,
        directory: Path | str,
        output: Path | None = None,
        max_depth: int = 0,
        sort_order: str = "files",
        metadata: str = "none",
        disable_color: bool = False,
        output_format: list | None = None,
        gitignore_path: Path | None = None,
        exclude: list[str] | None = None,
        no_console: bool = False,
        icons: str = "emoji",
        replace_path: Path | None = None,
        replace_tag: str | None = None,
    ) -> None:
        """Initialize the RichTree with a directory, optional output file, maximum depth, and sort order."""
        self.root = Path(directory)
        self.output: Path | None = output
        self.max_depth: int = abs(max_depth)
        self.sort_order: str = sort_order
        self.metadata: str = metadata
        self.file_count = 0
        self.dir_count = 0
        self.ignore_handler = IgnoreHandler(gitignore_path)
        _console_icons: IconMode = IconMode[icons.upper() + "_ICONS"]
        self.icon = IconManager(mode=_console_icons)
        if exclude:
            self.ignore_handler.add_patterns(exclude)
        self.output_format: list[str] = output_format or ["text"]
        self.disable_color: bool = disable_color
        self.no_console: bool = no_console
        self.output_console: Console = get_console(disable_color)
        self.replace_path = replace_path
        self.replace_tag = replace_tag
        self.tree = Tree(f"{self.icon.folder_default}  {self.root.resolve().name}")

    def get_file_string(self, item: Path) -> str:
        """Generate a string representation of a file with its metadata."""
        item_string = f"{self.icon.get(item)} {item.name}"
        if self.metadata == "none":
            return item_string
        if self.metadata in ["size", "all"]:
            file_size = item.stat().st_size
            item_string += f" ({file_size} bytes)"
        if self.metadata in ["lines", "all"]:
            try:
                number_of_lines: int = len(item.read_text(encoding="utf-8").splitlines())
                item_string += f" ({number_of_lines} lines)"
            except UnicodeDecodeError:
                item_string += " (binary)"
        return item_string

    def get_items(self, path: Path) -> list[Path]:
        """Get items in the directory, sorted by the specified order."""
        return (
            (sorted(path.iterdir(), key=lambda x: (x.is_dir(), x.name.lower())))
            if self.sort_order == "files"
            else sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
        )

    def add_to_tree(self, path: Path, tree_node: Tree, current_depth: int = 0) -> None:
        """Recursively add items to the tree structure."""
        if self.max_depth and current_depth >= self.max_depth:
            return

        for item in self.get_items(path):
            if self.ignore_handler.should_ignore(item):
                continue
            if item.is_dir():
                branch = (
                    tree_node.add(f"{self.icon.get(item)} {item.name}", highlight=True, style="bold green")
                    if not self.disable_color
                    else tree_node.add(f"{item.name}")
                )
                self.dir_count += 1
                self.add_to_tree(item, branch, current_depth + 1)
            else:
                (
                    tree_node.add(self.get_file_string(item), highlight=False, style="dim white")
                    if not self.disable_color
                    else tree_node.add(self.get_file_string(item))
                )
                self.file_count += 1

    @property
    def totals(self) -> str:
        """Return a string with the total counts of directories and files."""
        return f"{self.dir_count} directories, {self.file_count} files"

    def run(self) -> RunResult:
        """Build the tree and return results for the :class:`OutputManager`."""
        self.add_to_tree(path=self.root, tree_node=self.tree)
        return RunResult(tree=self.tree, totals=self.totals, cli=self)


def get_args() -> Namespace:
    """Parse command line arguments."""
    parser = ArgumentParser(
        description="Display a directory tree in a rich format.",
        prog="rTree",
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory to display",
    )

    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=None,
        help="Output file path, the extension will be determined by the output format, default is None (console output only)",
    )

    parser.add_argument(
        "--max_depth",
        "--depth",
        "--level",
        "-d",
        "-l",
        type=int,
        default=0,
        help="Maximum depth of the tree (0 for no limit)",
    )

    parser.add_argument(
        "--sort_order",
        "-s",
        choices=["files", "dirs"],
        default="files",
        help="Order of items in the tree (default: files)",
    )

    parser.add_argument(
        "--metadata",
        "-m",
        choices=["none", "all", "size", "lines"],
        default="none",
        help="Metadata to display for files (default: none)",
    )

    parser.add_argument(
        "--disable_color",
        "-dc",
        action="store_true",
        help="Disable colored output",
    )

    parser.add_argument(
        "--gitignore_path",
        "--gitignore",
        "-g",
        default=None,
        help="Path to .gitignore file",
    )

    parser.add_argument(
        "--exclude",
        "-e",
        default=None,
        nargs="+",
        help="Exclude files or directories matching this pattern",
    )

    parser.add_argument(
        "--output_format",
        "-f",
        choices=OutputFormat.choices(),
        nargs="+",
        default=OutputFormat.default(),
        help=(f"Output format(s). Can specify multiple: --format {' '.join(OutputFormat.choices())} (default: text)"),
    )

    parser.add_argument(
        "--icons",
        "-i",
        type=str,
        default="emoji",
        choices=["plain", "emoji", "glyphs"],
        help=(
            "Format of console output. "
            "'plain' for no icons, "
            "'emoji' for emoji icons, "
            "'glyphs' for rich glyphs (default: emoji)"
        ),
    )

    parser.add_argument(
        "--no_console",
        "-no",
        action="store_true",
        help="Disable console output",
    )

    parser.add_argument(
        "--replace_path",
        "-r",
        type=str,
        default=None,
        help="File path of file to inject into the output tree. "
        "Typically with in markdown or html files. "
        "Content inside tags like '<!-- rTree -->{{ content replaced }}<!-- /rTree -->' "
        "will be replaced with the tree output.",
    )

    parser.add_argument(
        "--replace_tag",
        "-rt",
        type=str,
        default=None,
        help=(
            "Tag used for replacement. Provide a full tag pair like '<replace>'"
            " or '<!-- rTree -->'. Closing tag is inferred."
        ),
    )

    parser.add_argument(
        "--version",
        "-v",
        action="version",
        version=f"rTree v{__version__}",
        help="Show the version of rTree",
    )

    return parser.parse_args()


def main() -> None:
    """Main function to run the RichTreeCLI."""
    args: Namespace = get_args()
    args.directory = Path(args.directory)
    args.output = Path(args.output) if args.output else None
    output_manager = OutputManager(disable_color=args.disable_color)
    if not args.directory.is_dir() or not args.directory.exists():
        output_manager.error(f"Error: {args.directory} is not a valid directory.")
        sys.exit(1)

    args.gitignore_path = Path(args.gitignore_path) if args.gitignore_path else None
    args.replace_path = Path(args.replace_path) if args.replace_path else None
    args.replace_tag = args.replace_tag

    cli = RichTreeCLI(**vars(args))

    result: RunResult = cli.run()
    output_manager.set_cli(cli)
    output_manager.output(result=result, output_formats=args.output_format, output_path=args.output)


if __name__ == "__main__":
    main()
