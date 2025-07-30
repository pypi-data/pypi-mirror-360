from instaui.components.element import Element
from instaui.vars.types import TMaybeRef


def teleport(
    to: TMaybeRef[str],
    *,
    defer: bool = True,
    disabled: TMaybeRef[bool] = False,
):
    """
    Creates a teleport element that can be used to move a component to a different part of the DOM.


    """
    ele = Element(tag="teleport")
    ele.props({"to": to})

    if defer is not True:
        ele.props({"defer": False})

    if disabled is not False:
        ele.props({"disabled": disabled})

    return ele
