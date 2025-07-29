from rich.console import Console
from rich.theme import Theme

_theme = Theme({
    "default": "",
    "error": "red",
    "list": "blue",
    "alt": "italic"
})

console = Console(emoji=False, theme=_theme)
econsole = Console(emoji=False, theme=_theme, stderr=True)
