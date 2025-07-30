from instaui.runtime import in_default_app_slot, HtmlResource


def use_tailwind(value=True):
    """Use Tailwind CSS framework.

    Args:
        value (bool, optional):  whether to use Tailwind CSS. Defaults to True.
    """

    if not in_default_app_slot():
        raise ValueError("Cannot set use_tailwind outside of ui.page")
    HtmlResource.use_tailwind = value
