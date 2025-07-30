from typing import Dict
from instaui import ui
from instaui.components import html
from instaui.vars.mixin_types.observable import ObservableMixin


def list_all_bindables(locals_dict: Dict):
    """List all bindables in the locals() dictionary.


    Example usage:

    ```python
    list_all_bindables(locals())
    ```

    """

    with html.div().style(
        "display: grid; grid-template-columns: auto 1fr; border: 1px solid black; padding: 10px;"
    ):
        html.label("variable name")
        html.label("bindable value").style("justify-self: center;")

        html.div().style(
            "grid-column: 1 / span 2;height: 1px;border-bottom: 1px solid black;"
        )

        for key, value in locals_dict.items():
            if isinstance(value, ObservableMixin):
                cp_value = ui.js_computed(
                    inputs=[value],
                    code=r"""(obj)=>{
 
    if (typeof obj === 'object') {
        if (obj === null) {
            return 'null';
        } else {
            return JSON.stringify(obj);
        }
    } else {
        return String(obj);
    }
}""",
                )

                html.paragraph(f"{key}:").style("justify-self: end;")
                html.paragraph(cp_value).style("justify-self: center;")
