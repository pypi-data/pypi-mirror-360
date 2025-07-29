from budget.table import Table
from jinja2 import Environment, PackageLoader, select_autoescape

from ._renderer import Renderer


class JinjaRenderer(Renderer):
    def __init__(self, template: str):
        self._template = template
        self.env = Environment(
            loader=PackageLoader("budget.rendering", "templates"),
            autoescape=select_autoescape(),
        )

    def render_table(self, table: Table):
        layout = self.env.get_template(self._template)
        print(layout.render(table=table))
