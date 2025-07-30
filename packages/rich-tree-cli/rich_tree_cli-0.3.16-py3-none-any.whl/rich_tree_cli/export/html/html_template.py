"""Load the HTML template for rendering output."""

from pathlib import Path

from jinja2 import Template

TEMPLATE_PATH: Path = Path(__file__).parent / "assets" / "template.jinja2"
HTML_TEMPLATE: Template = Template(TEMPLATE_PATH.read_text(encoding="utf-8"))
STYLES_CSS: str = Path(TEMPLATE_PATH.parent / "styles.css").read_text(encoding="utf-8")
