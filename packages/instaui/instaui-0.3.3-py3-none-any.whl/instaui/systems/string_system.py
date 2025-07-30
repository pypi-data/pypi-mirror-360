def is_async_js_function(js_code: str):
    js_code = js_code.strip()

    if js_code.startswith("async "):
        return True

    if js_code.startswith("async(") or js_code.startswith("async ("):
        return True

    return False
