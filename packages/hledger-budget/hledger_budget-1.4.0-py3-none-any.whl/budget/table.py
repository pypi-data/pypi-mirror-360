from dataclasses import dataclass, field
from typing import Any, Literal


@dataclass
class Text:
    lines: str | list[str]
    style: str = "default"
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not isinstance(self.lines, (str, list, tuple)):
            self.lines = str(self.lines)

    @classmethod
    def from_any(cls, lhs) -> "Text":
        if not isinstance(lhs, Text):
            return Text(lhs)
        return lhs

    @property
    def text(self) -> str:
        return self.get_text()

    def get_text(self, sep: str = " ") -> str:
        if isinstance(self.lines, str):
            return self.lines
        return sep.join(self.lines)


@dataclass
class ColumnStyle:
    justify: Literal["default", "left", "center", "right", "full"] = "left"


class Table:
    def __init__(self, title=None):
        self.title: str | None = title
        self.header: list[Text] = []
        self.rows: list[list[Text]] = []
        self.footer: tuple[Text, ...] = ()
        self.styles: list[ColumnStyle] = []

    def add_column(
        self,
        *cells,
        header: Text | str | list[str] = "",
        style: ColumnStyle | None = None
    ):
        if self.rows and len(cells) != len(self.rows):
            raise ValueError("number of items doesn't match number of rows")
        if not self.rows:
            self.rows = [[] for _ in cells]

        if style is None:
            style = ColumnStyle()

        for i, cell in enumerate(cells):
            self.rows[i].append(Text.from_any(cell))

        self.header.append(Text.from_any(header))
        self.styles.append(style)

    def add_row(self, *cells: str | Text):
        if self.rows and len(self.rows[0]) != len(cells):
            raise ValueError("number of items doesn't match number of columns")

        self.rows.append([Text.from_any(cell) for cell in cells])

    def set_footer(self, *data):
        if len(data) != len(self.header):
            raise ValueError("invalid number of items in footer")
        self.footer = tuple(Text.from_any(d) for d in data)
