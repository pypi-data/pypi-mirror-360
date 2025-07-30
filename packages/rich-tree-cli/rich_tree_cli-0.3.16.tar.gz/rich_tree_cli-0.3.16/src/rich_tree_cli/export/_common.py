from enum import StrEnum
from pathlib import Path

ICON_DIR: Path = Path(__file__).parent / "html" / "assets" / "icons"

OB = "{{ "
CB = " }}"


def jinja_template(txt: str) -> str:
    """Wrap text in curly braces for templating, unless already wrapped."""
    if not txt.startswith(OB) and not txt.endswith(CB):
        return OB + txt + CB
    return txt


class URIScheme(StrEnum):
    """Enum for URI schemes."""

    FILE = "file:///"
    VSC_IN = "vscode-insiders://file"


FILE = URIScheme.FILE
VSC_IN = URIScheme.VSC_IN
