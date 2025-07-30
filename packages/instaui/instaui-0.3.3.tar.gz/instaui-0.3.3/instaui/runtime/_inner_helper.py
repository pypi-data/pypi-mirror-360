from instaui.runtime.context import get_context


def check_web_only_mode_or_error(method_name: str = ""):
    mode = get_context().app_mode
    if mode != "web" and mode != "webview":
        raise Exception(
            f"{method_name} This is a web-only feature. Please use the 'web' or 'webview' mode."
        )
