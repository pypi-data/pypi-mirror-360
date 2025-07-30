from datetime import datetime
from typing import Optional, Union
from instaui.runtime.context import get_context


def cookie_output():
    if not get_context().app_mode == "web":
        raise ValueError("cookie_output can only be used in web mode")


def cookie_input():
    pass


def set_cookie(
    key: str,
    value: str,
    *,
    max_age: Optional[int] = None,
    expires: Optional[Union[int, datetime]] = None,
    secure: bool = False,
    httponly: bool = False,
    samesite: Optional[str] = None,
):
    pass
