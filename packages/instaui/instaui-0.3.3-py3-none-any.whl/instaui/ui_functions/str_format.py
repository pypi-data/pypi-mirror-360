from typing import cast
from instaui.vars.mixin_types.str_format_binding import StrFormatBindingMixin
from instaui.vars.vue_computed import VueComputed


def str_format(template: str, *args, **kwargs):
    bindings = {}

    tran_args = []

    for idx, arg in enumerate(args):
        is_mixin = isinstance(arg, StrFormatBindingMixin)
        value = (
            cast(StrFormatBindingMixin, arg)._to_str_format_binding(idx)
            if is_mixin
            else arg
        )
        tran_args.append(value[-1] if is_mixin else value)
        if is_mixin:
            bindings[value[0]] = arg

    tran_kwargs = {}

    for idx, (k, v) in enumerate(kwargs.items()):
        is_mixin = isinstance(v, StrFormatBindingMixin)
        value = (
            cast(StrFormatBindingMixin, v)._to_str_format_binding(idx)
            if is_mixin
            else v
        )
        tran_kwargs[k] = value[-1] if is_mixin else value
        if is_mixin:
            bindings[value[0]] = v

    code = "()=>`" + template.format(*tran_args, **tran_kwargs) + "`"
    return VueComputed(code, bindings=bindings)
