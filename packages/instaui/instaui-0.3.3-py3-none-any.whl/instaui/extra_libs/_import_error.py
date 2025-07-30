def show_error(msg: str):
    def error_handler(error: Exception):
        from instaui.components.html.paragraph import Paragraph

        Paragraph(msg).style(
            "border: 1px dashed red;padding: 1em;font-weight: bold;font-size: medium;"
        )

    return error_handler
