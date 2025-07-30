from typing import Callable

def get_key_name(entry, *args):
    for arg in args:
        if arg in entry:
            return f"arg:{entry[arg]}"

def default_dict_key_extractor(entry):
    if isinstance(entry, dict):
        for key in ('id', 'ID', 'uuid', 'UUID'):
            if key in entry:
                return f"{key}={entry[key]}"
