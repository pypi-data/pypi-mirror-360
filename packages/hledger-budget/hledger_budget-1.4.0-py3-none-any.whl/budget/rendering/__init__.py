from enum import Enum

from ._renderer import Renderer
from .csv import CSVRenderer
from .jinja import JinjaRenderer
from .rich import RichRenderer


class OutputType(Enum):
    rich = "rich"
    csv = "csv"
    html = "html"
    html_bare = "html-bare"
    dokuwiki = "dokuwiki"


def render(output_type, *objects):
    renderer: Renderer | None = None
    match OutputType(output_type):
        case OutputType.rich:
            renderer = RichRenderer()
        case OutputType.csv:
            renderer = CSVRenderer()
        case OutputType.html:
            renderer = JinjaRenderer("html_full.html")
        case OutputType.html_bare:
            renderer = JinjaRenderer("html_bare.html")
        case OutputType.dokuwiki:
            renderer = JinjaRenderer("dokuwiki.txt")
        case _:
            raise ValueError(f"unknown renderer: {output_type}")

    for obj in objects:
        renderer.render(obj)
