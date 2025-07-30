from pathlib import Path
from instaui.runtime._app import get_app_slot


_STATIC_DIR = Path(__file__).parent / "static"
_CSS_FILE = _STATIC_DIR / "shadcn-classless.css"


def use_shadcn_classless(value=True):
    """Use shadcn-classless.css or not.

    Args:
        value (bool, optional): Whether to use shadcn-classless.css or not. Defaults to True.

    Example:

    App default use shadcn-classless.css:
    .. code-block:: python

        @ui.page('/')
        def index():

            # Create a container with shadcn-classless class
            with html.div().classes("shadcn-classless"):
                html.h1("Hello, world!")

                with html.form():
                    html.input()
                    html.button("Submit")

    Can be disabled:
    .. code-block:: python
        # App does not use shadcn-classless
        ui.use_shadcn_classless(False)

    """

    if value:
        get_app_slot()._html_resource.add_css_link(_CSS_FILE)

    else:
        get_app_slot()._html_resource.remove_css_link(_CSS_FILE)
