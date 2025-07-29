"""
File: util.py
Description: Util module.
CreateDate: 2024/5/12
Author: xuwenlin
E-mail: wenlinxu.njfu@outlook.com
"""
from typing import Callable
from natsort import natsort_key


class FuncDict(dict):
    def sort_by_keys(self, key: Callable = natsort_key,  reverse: bool = False):
        sorted_dict = FuncDict({key: self[key] for key in sorted(self, key=key, reverse=reverse)})
        self.clear()
        self.update(sorted_dict)

    def __getitem__(self, key):
        """Returns the same value as the key when a non-existent key is accessed."""
        try:
            return super().__getitem__(key)
        except KeyError:
            return key

    def __add__(self, other):
        for k, v in other.items():
            if k in self:
                self[k] += v
            else:
                self[k] = v
