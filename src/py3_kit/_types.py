from abc import ABCMeta
from collections.abc import ItemsView, KeysView, ValuesView
from types import new_class
from typing import NamedTuple, cast

import py3_kit


class ViewClasses(NamedTuple):
    ItemsView: type
    KeysView: type
    ValuesView: type


def create_view_classes(class_name: str) -> ViewClasses:
    def _create_view_classes(base_class: type) -> type:
        name = f"{class_name}{base_class.__name__}"
        return new_class(
            name,
            (base_class,),
            exec_body=lambda ns: ns.update({
                "__repr__": lambda self: f"{py3_kit.string.camel_to_snake(name)}({list(self)})"
            })
        )

    return ViewClasses(
        ItemsView=_create_view_classes(ItemsView),
        KeysView=_create_view_classes(KeysView),
        ValuesView=_create_view_classes(ValuesView),
    )


def create_subclasscheck_meta_class(
        meta_class_name: str = "SubclasscheckMeta",
        *,
        required_all_methods: tuple[str, ...] = tuple(),
        required_any_methods: tuple[str, ...] = tuple()
) -> type[ABCMeta]:
    return cast(type[ABCMeta], new_class(
        meta_class_name,
        (ABCMeta,),
        exec_body=lambda ns: ns.update({
            "__subclasscheck__": classmethod(
                lambda cls, subclass:
                all([callable(getattr(subclass, i, None)) for i in required_all_methods]) and
                (any([callable(getattr(subclass, i, None)) for i in required_any_methods]) if required_any_methods
                 else True)
            )
        })
    ))
