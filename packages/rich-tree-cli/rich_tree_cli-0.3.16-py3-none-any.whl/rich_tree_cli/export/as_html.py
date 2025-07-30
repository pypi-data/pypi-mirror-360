"""# Python module to export directory structures as HTML for RichTreeCLI."""

from hashlib import blake2b
from io import StringIO
from pathlib import Path
from types import SimpleNamespace
from typing import TYPE_CHECKING
from urllib.parse import quote

from jinja2 import Template
from rich.console import Console
from rich.tree import Tree

from ._common import VSC_IN, URIScheme, jinja_template as jt
from .html.html_template import HTML_TEMPLATE, STYLES_CSS
from .icons import IconManager, IconMode

if TYPE_CHECKING:
    from rich_tree_cli.main import RichTreeCLI

css_classes = SimpleNamespace()
css_classes.folder = "class='folder'"
css_classes.file = "class='file'"
css_classes.hidden = "class='hidden'"


def _hash(txt: str, length: int = 20) -> str:
    return "h" + blake2b(txt.encode(encoding="utf-8"), digest_size=length // 2).hexdigest()


def build_html(cli: "RichTreeCLI") -> str:
    """Build an HTML representation of the directory structure for RichTreeCLI."""
    html_template = HTMLHandler(cli=cli)
    return html_template.render()


class HTMLHandler:
    """Class to handle HTML export of the directory structure for RichTreeCLI."""

    def __init__(self, cli: "RichTreeCLI", uri_mode: URIScheme = VSC_IN) -> None:
        """Initialize the HTMLHandler with a RichTreeCLI instance."""
        self.cli: RichTreeCLI = cli
        self.icon = IconManager(mode=IconMode.SVG_ICONS)
        self.root: Path = cli.root.resolve()
        self.template_map: SimpleNamespace = SimpleNamespace()
        self.tree = Tree(self.link(path=self.root, uri=uri_mode, cls_name=css_classes.folder), highlight=True)
        self.capture: Console = Console(record=True, markup=False, file=StringIO(), emoji=True, soft_wrap=False)
        self.add_to_html_tree(path=cli.root, tree_node=self.tree, current_depth=cli.max_depth)
        self.capture.print(self.tree)

    def link(self, path: Path, uri: URIScheme, cls_name: str) -> str:
        """Create a link and return a Jinja2 hash reference to avoid Rich formatting issues.

        Generates an HTML link with icon and styling, stores it in the template map using
        a hash as the attribute name, and returns {{ hash.{href_hash} }} for dot notation
        access in Jinja2 templates. This keeps Rich trees clean while preserving full links.

        Args:
            path (Path): The file path to link to.
            uri (URIScheme): The URI scheme to use, e.g., FILE or VSC_IN.
            cls_name (str): CSS class to apply to the link.

        Returns:
            str: Jinja2 template variable "{{ hash.{href_hash} }}" for dot notation access.

        Raises:
            ValueError: If a hash collision is detected.
        """
        label: str = f"{self.icon.get(path)} {path.name}"
        a_href = '<a href="{url}" {cls}>{label}</a>'
        link: str = f"{uri}{quote(str(path.resolve()), safe='/')}"
        a_href: str = a_href.format(url=link, cls=cls_name, label=label)
        href_hash: str = _hash(a_href)
        if hasattr(self.template_map, href_hash):
            raise ValueError(f"WEE WOO! Hash collision detected: {href_hash} for {path}. WEE WOO!")
        setattr(self.template_map, href_hash, a_href)
        return jt(f"hash.{href_hash}")

    def add_to_html_tree(self, path: Path, tree_node: Tree, current_depth: int = 0) -> Tree:
        """Recursively add items to the tree structure.

        Args:
            path (Path): The current directory path.
            tree_node (Tree): The current tree node to add items to.
            current_depth (int): The current depth in the directory structure.

        Returns:
            Tree: The updated tree node with items added.
        """
        if self.cli.max_depth and current_depth >= self.cli.max_depth:
            return tree_node

        for item in self.cli.get_items(path):
            if self.cli.ignore_handler.should_ignore(item):
                continue
            if item.is_dir():
                branch: Tree = tree_node.add(
                    label=self.link(path=item, uri=VSC_IN, cls_name=css_classes.folder), highlight=True
                )
                self.add_to_html_tree(path=item, tree_node=branch, current_depth=current_depth + 1)
            else:
                file: str = self.link(path=item, uri=VSC_IN, cls_name=css_classes.file)
                hidden: str = self.link(path=item, uri=VSC_IN, cls_name=css_classes.hidden)
                cls_func: str = hidden if item.name.startswith(".") else file
                tree_node.add(label=cls_func, highlight=False)
        return tree_node

    def render(self) -> str:
        """Build HTML output from the captured console output.

        Args:
            capture (Console): The console object that has captured the output.

        Returns:
            str: The HTML formatted string.
        """
        tree = self.capture.export_text()
        ##########################
        ### FOR DEBUGGING ONLY ###
        # with open("hash_test.txt", "w", encoding="utf-8") as f:
        #     f.write(tree)
        ##########################
        html = Template(
            HTML_TEMPLATE.render(
                defined_css=STYLES_CSS,
                tree_content=tree,
                totals=self.cli.totals,
            )
        )

        return html.render(hash=self.template_map)
