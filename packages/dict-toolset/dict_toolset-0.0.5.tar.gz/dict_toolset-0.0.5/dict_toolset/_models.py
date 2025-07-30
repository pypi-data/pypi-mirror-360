from __future__ import annotations


class Key:

    __slots__ = ["name", "value", "value_type", "parent", "children"]

    def __init__(
        self,
        name: str = None,
        value: any = None,
        value_type: type = None,
        parent: Key = None,
        children: list[Key] = None
    ) -> None:
        self.name = name
        self.value = value
        self.value_type = value_type
        self.parent = parent
        self.children = children


