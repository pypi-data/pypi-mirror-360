"""Python module to manage output for RichTreeCLI, including file exports and console rendering."""

from io import StringIO
import json
from pathlib import Path
from typing import TYPE_CHECKING

from rich.console import Console

from ._get_console import get_console
from .constants import OutputFormat, RunResult
from .export.as_html import build_html
from .export.as_json import build_json
from .export.as_toml import build_toml
from .export.as_xml import build_xml
from .export.as_yaml import build_yaml
from .export.replace_tags import output_to_file

if TYPE_CHECKING:
    from rich_tree_cli.main import RichTreeCLI


class OutputManager:
    """Handle writing output files and rendering to the console."""

    def __init__(self, disable_color: bool = False) -> None:
        """Initialize the OutputManager with an optional color setting."""
        self.console: Console = get_console(disable_color)
        self.disable_color = disable_color
        self.no_console = False
        self.cli = None  # type: ignore[assignment] | this will be set later

    def set_cli(self, cli: "RichTreeCLI") -> None:
        """Set the CLI instance for the output manager."""
        self.cli: RichTreeCLI = cli
        self.disable_color: bool = cli.disable_color
        self.no_console: bool = cli.no_console

    @staticmethod
    def get_ext(fmt: str) -> str:
        """Get the file extension based on the output format, check the OutputFormat enum."""
        try:
            return f".{OutputFormat.key_to_value(fmt)}"
        except ValueError:
            return ".txt"

    def generate_output(self, fmt: str, totals: str) -> str:
        """Generate the output in the specified format."""
        if self.cli is None:
            raise ValueError("CLI instance is not set. Call set_cli() before generating output.")

        capture: Console = get_console(disable_color=True, record=True, file=StringIO())
        output_buffer: StringIO = capture.file  # type: ignore | this is the reality but the type checker doesn't like it
        capture.print(self.cli.tree)
        result = output_buffer.getvalue()
        if fmt == "toml":
            result = self.to_toml()
        if fmt == "html":
            result: str = self.to_html(self.cli)
        if fmt == "markdown":
            result = self.to_markdown(result, totals)
        if fmt == "json":
            result = self.to_json(self.cli)
        if fmt == "svg":
            result = self.to_svg(capture)
        if fmt == "yaml":
            result = self.to_yaml()
        if fmt == "xml":
            result = self.to_xml(self.cli)
        output_buffer.close()
        return result or capture.export_text()

    def to_toml(self) -> str:
        """Render the tree and totals to a TOML string."""
        json_output: str = self.to_json(self.cli)
        return build_toml(json_data=json.loads(json_output))

    def to_yaml(self) -> str:
        """Render the tree and totals to a YAML string."""
        json_output: str = self.to_json(self.cli)
        return build_yaml(json_data=json.loads(json_output))

    @staticmethod
    def to_svg(capture: Console) -> str:
        """Render the tree and totals to an SVG string."""
        return capture.export_svg()

    @staticmethod
    def to_html(cli: "RichTreeCLI") -> str:
        """Render the tree and totals to an HTML string."""
        return build_html(cli)

    @staticmethod
    def to_markdown(export_text: str, totals: str) -> str:
        """Render the tree and totals to a markdown string."""
        return f"# Directory Structure\n\n```plain\n{export_text}\n```\n\n{totals}\n"

    @staticmethod
    def to_json(cli: "RichTreeCLI") -> str:
        """Render the tree and totals to a JSON string."""
        return json.dumps(build_json(cli, cli.root), indent=2)

    @staticmethod
    def to_xml(cli: "RichTreeCLI") -> str:
        """Render the tree and totals to an XML string."""
        return build_xml(cli)

    @staticmethod
    def to_console(result: RunResult, console: Console, disable_color: bool, no_console: bool) -> None:
        """Render the tree and totals to the console."""
        if no_console:
            return

        if disable_color:
            console.print(result.tree, highlight=False)
            console.print(f"\n{result.totals}\n", highlight=False)
        else:
            console.print(result.tree)
            console.print(f"\n{result.totals}\n", style="bold green")

    def output(self, result: RunResult, output_formats: list[str], output_path: Path | None) -> None:
        """Write files and render console output."""
        if output_path is not None:
            for fmt in output_formats:
                out_str: str = self.generate_output(fmt, result.totals)
                ext: str = self.get_ext(fmt)
                out_file: Path = output_path.with_name(f"{output_path.stem}{ext}")
                out_file.write_text(out_str, encoding="utf-8")
        self.to_console(result, self.console, self.disable_color, self.no_console)
        if self.cli.replace_path:
            output_to_file(self, self.cli)

    def info(self, message: str) -> None:
        """Display an informational message."""
        self.console.print(message, style="bold blue")

    def error(self, message: str) -> None:
        """Display an error message."""
        self.console.print(message, style="bold red")
