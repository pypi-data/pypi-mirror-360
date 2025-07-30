from typing import Callable


def _merge(
    *args: dict | list,
    add_list_index: bool = True
) -> dict | list:
    """Merge a custom list of dictionaries and lists. In case that the input 
    list contains one list, the output will always be a list. In case that the 
    input does not contain any list, the output will be a dictionary.

    Returns:
        dict | list: a merged dictionary or list
    """
    row = {}
    table = []
    for entry in args:
        if isinstance(entry, list):
            table += entry
        elif isinstance(entry, dict):
            row |= entry
    if not row:
        return table
    if not table:
        return row
    return [
        row | (entry or {}) | ({"index": index} if add_list_index else {})
        for index, entry in enumerate(table)
    ]


class FilterValue():
    def __init__(self, value) -> None:
        self.value = value

    def __eq__(self, other) -> bool:
        return (
            type(self) == type(other)
            and self.value == other.value
        )


class FilterType():
    def __init__(self, value) -> None:
        self.value = value

    def __eq__(self, other) -> bool:
        return (
            type(self) == type(other)
            and self.value == other.value
        )


def _filter(conditions: list[tuple], key: tuple, value: any):
    if not key or not conditions:
        return None

    variations = [
        key,
        key + (FilterType(type(value)),),
        key + (FilterValue(value),),
    ]

    return any(condition in variations for condition in conditions)


def tabulate(
    data: any,
    current_key: tuple = None,
    exclude_keys: list[tuple] = None,
    key_converter: Callable[[tuple], any] = None,
    add_list_index: bool = True
) -> list | dict:
    """Convert a list or a dictionary recursively to a table formatted output. 
    E.g. use the ouput to write it into a csv file (using the CsvDictWriter)

    :param data: pass the input data which should be a list or a dictionary
    :type data: any
    :param current_key: pass a key or an identifier which is used as prefix, 
        defaults to None
    :type current_key: tuple, optional
    :param exclude_keys: define a list of keys as tuples which should be 
        excluded from the ouput data, defaults to None
    :type exclude_keys: list[tuple], optional
    :param key_converter: define a function to convert the given key tuple.
        E.g. you can create a . separated key name. By default the key is kept 
        as tuple, defaults to None
    :type key_converter: Callable[[tuple], any], optional
    :param add_list_index: _description_, defaults to True
    :type add_list_index: bool, optional
    :return: The function will return list or a dict based on the input data
    :rtype: list | dict
    """
    excluded = _filter(exclude_keys, current_key, data)
    if (excluded is not None and excluded is True):
        return None

    if current_key is None:
        current_key = tuple()

    if isinstance(data, list):
        entries = [[
            tabulate(
                entry,
                current_key,
                exclude_keys,
                key_converter,
                add_list_index
            ) for entry in data
        ]]
    elif isinstance(data, dict):
        entries = [
            tabulate(
                entry,
                current_key + (key,),
                exclude_keys,
                key_converter,
                add_list_index
            ) for key, entry in data.items()
        ]
    else:
        if key_converter:
            current_key = key_converter(current_key)
        entries = [{current_key: data}]

    return _merge(*entries, add_list_index=add_list_index)


def get_columns(table: list | dict) -> set:
    """A function to get all key from an list or dictionary on it's first level

    :param table: the input data
    :type table: list | dict
    :return: a set of unique keys
    :rtype: set
    """
    if isinstance(table, dict):
        return set(table.keys())
    return set(key for row in table for key in row)
