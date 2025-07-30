from typing import Callable

from ._key_extractor import default_dict_key_extractor
from ._basic import get_key, list_to_dict


def _get_from_list(
    index,
    entries,
    key_extractors: list[Callable]
):
    for entry_index, entry in enumerate(entries):
        entry_key = get_key(entry, key_extractors) or entry_index
        if entry_key == index:
            return entry_index, entry

def merge(
    data_a,
    data_b,
    key_extractors: list[Callable] = [default_dict_key_extractor]
):
    type_a = type(data_a)
    type_b = type(data_b)

    if type_a != type_b:
        raise TypeError('Types a incompatible to merge')

    rtn = None

    if type_a == dict:
        rtn = {}
        for key, value in data_a.items():
            type_a = type(value)
            if type_a in [dict, list]:
                rtn[key] = merge(data_a[key], data_b[key])
            else:
                rtn[key] = value
        for key, value in data_b.items():
            if key not in data_a:
                rtn[key] = value
        return rtn
    elif type_a == list:
        dict_data_a = list_to_dict(data_a, key_extractors)
        dict_data_b = list_to_dict(data_b, key_extractors)
        merged_dict = merge(dict_data_a, dict_data_b, key_extractors)
        return list(merged_dict.values())
