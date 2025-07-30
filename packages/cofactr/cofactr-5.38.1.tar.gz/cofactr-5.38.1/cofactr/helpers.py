"""Helper functions."""
# Standard Modules
from functools import reduce
from operator import getitem


def get_path(data, keys, default=None):
    """Access a nested dictionary."""
    try:
        return reduce(getitem, keys, data)
    except (KeyError, IndexError):
        return default


identity = lambda x: x
