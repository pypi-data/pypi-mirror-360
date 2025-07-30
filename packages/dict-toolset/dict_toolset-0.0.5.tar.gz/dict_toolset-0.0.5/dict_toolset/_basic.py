from typing import Callable


def get_key(data: any, key_extractors: list[Callable]) -> any:
    """Extract the key with a given list of key extractors

    :param data: input data
    :type data: any
    :param key_extractors: a list of key extractors
    :type key_extractors: list[Callable]
    :return: return the key
    :rtype: any
    """
    for key_extractor in key_extractors:
        if key := key_extractor(data):
            return key

def list_to_dict(input: list, key_extractors: list[Callable] = []) -> dict:
    """Convert a list into a dictionary using the given key extractors

    :param input: the input list
    :type input: list
    :param key_extractors: a list of key extractors, defaults to []
    :type key_extractors: list[Callable], optional
    :return: returns a dictionary
    :rtype: dict
    """
    rtn = {}
    for index, entry in enumerate(input):
        index = get_key(entry, key_extractors) or index
        rtn[f"[{index}]"] = entry
    return rtn

def extend_list(input: list, index: int):
    """
    Extends the given list to ensure it has at least 'index + 1' elements.

    Any additional elements are filled with 'None'.

    Parameters:
    :param list input: The list to be extended.
    :param int index: The index of the element to retrieve from the extended list.

    Returns:
    :return: The value at the specified 'index' in the extended list.
    :rtype: Any

    Example:
    >>> extend_list([1, 2, 3], 5)
    [1, 2, 3, None, None, None]

    >>> extend_list(['a', 'b', 'c'], 2)
    'c'
    """
    if (diff := (index + 1) - len(input)) > 0:
        input.extend([None for i in range(diff)])
    return input[index]
