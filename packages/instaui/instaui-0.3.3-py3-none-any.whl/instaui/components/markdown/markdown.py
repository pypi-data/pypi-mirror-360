from pathlib import Path
from instaui import ui

_STATIC_DIR = Path(__file__).parent / "static"
_CORE_JS_FILE = _STATIC_DIR / "marked.esm.js"
_GITHUB_MARKDOWN_CSS_FILE = _STATIC_DIR / "github-markdown.css"

_IMPORT_MAPS = {
    "marked": _CORE_JS_FILE,
}


class Markdown(
    ui.element,
    esm="./markdown.js",
    externals=_IMPORT_MAPS,
    css=[_GITHUB_MARKDOWN_CSS_FILE],
):
    def __init__(self, content: ui.TMaybeRef[str]):
        super().__init__()
        self.props({"content": _clean_multiline_string(content)})


def _clean_multiline_string(text: ui.TMaybeRef[str]) -> ui.TMaybeRef[str]:
    if not isinstance(text, str):
        return text

    if not text:
        return ""

    lines = text.splitlines()

    while lines and lines[0].strip() == "":
        lines.pop(0)
    while lines and lines[-1].strip() == "":
        lines.pop()

    if lines:
        lines[0] = lines[0].lstrip()

    return "\n".join(lines)
