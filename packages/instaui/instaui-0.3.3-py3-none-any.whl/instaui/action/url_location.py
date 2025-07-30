from urllib.parse import quote_plus


class UrlLocation:
    @staticmethod
    def goto(url: str, **params):
        url = _url_with_params(url, **params)
        return f'window.location.href = "{url}"'

    @staticmethod
    def replace(url: str, **params):
        url = _url_with_params(url, **params)
        return f'window.location.replace("{url}")'

    @staticmethod
    def back():
        return "window.history.back()"

    @staticmethod
    def forward():
        return "window.history.forward()"

    @staticmethod
    def reload():
        return "window.history.go(0)"


def _url_with_params(url: str, **params):
    url_params = "&".join([f"{k}={v}" for k, v in params.items()])
    if url_params:
        url += f"?{url_params}"

    return quote_plus(url, safe=":/?=&")
