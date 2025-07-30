from pathlib import Path
from typing import Literal

_THIS_DIR = Path(__file__).parent
_TEMPLATES_DIR = _THIS_DIR.joinpath("templates")
_STATIC_DIR = _THIS_DIR.joinpath("static")
_COMPILED_DIR = _STATIC_DIR.joinpath("compiled")

INDEX_TEMPLATE_PATH = _TEMPLATES_DIR.joinpath("index.html")
FAVICON_PATH = _STATIC_DIR.joinpath("insta-ui.ico")

# compiled files
APP_ES_JS_PATH = _COMPILED_DIR.joinpath("insta-ui.esm-browser.prod.js")
APP_ES_JS_MAP_PATH = _COMPILED_DIR.joinpath("insta-ui.js.map")
APP_CSS_PATH = _COMPILED_DIR.joinpath("insta-ui.css")
VUE_ES_JS_PATH = _COMPILED_DIR.joinpath("vue.esm-browser.prod.js")
# tools
TOOLS_BROWSER_JS_PATH = _COMPILED_DIR.joinpath("instaui-tools-browser.js")

PAGE_TITLE = "insta-ui"
SCOPED_STYLE_GROUP_ID = "insta-scoped-style"

_T_App_Mode = Literal["zero", "web", "webview"]
TModifier = Literal["trim", "number", "lazy"]
