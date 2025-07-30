from __future__ import annotations
import jinja2


env = jinja2.Environment(
    loader=jinja2.PackageLoader("instaui.static", "templates"),
)
