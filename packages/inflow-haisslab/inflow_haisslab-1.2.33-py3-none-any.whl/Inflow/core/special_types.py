# -*- coding: utf-8 -*-
"""
Created on Fri Feb 10 15:57:47 2023

@author: tjostmou
"""

from typing import List, Dict, Any


def make_hashable(dataframe):
    def to_hashable(cell):
        if isinstance(cell, list):
            return HashableList(cell)
        if isinstance(cell, dict):
            return HashableDict(cell)
        if isinstance(cell, set):
            return HashableSet(cell)
        return cell

    return dataframe.applymap(to_hashable)


class AttrDict(dict):
    # a class to make dictionnary keys accessible with attribute syntax
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


class IndexableList(list):  # a list you can get a subsection of as you would do with a pd dataframe or series
    # it expects a BOOLEAN index mask that matches the length of the list
    def __init__(self, iterable):
        super().__init__(iterable)

    def __getitem__(self, index):
        import pandas as pd, numpy as np

        if isinstance(index, (list, np.ndarray, pd.core.series.Series)) and len(index) == len(self):
            return IndexableList([item for item, selected in zip(self, index) if selected])
        return super().__getitem__(index)


class HashableList(list):
    def __init__(self, alist):
        content = []
        for item in alist:
            if isinstance(item, list):
                item = HashableList(item)
            elif isinstance(item, dict):
                item = HashableDict(item)
            elif isinstance(item, set):
                item = HashableSet(item)
            content.append(item)
        super().__init__(content)

    def __hash__(self):
        return hash(tuple(sorted(self, key=lambda item: item.__hash__())))

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

    def __lt__(self, other):
        return self.__hash__() < other.__hash__()

    def __gt__(self, other):
        return self.__hash__() > other.__hash__()


class HashableDict(dict):
    def __init__(self, adict):
        content = {}
        for key, value in adict.items():
            if isinstance(value, dict):
                value = HashableDict(value)
            elif isinstance(value, list):
                value = HashableList(value)
            elif isinstance(value, set):
                value = HashableSet(value)
            content[key] = value
        super().__init__(content)

    def __hash__(self):
        return hash(frozenset(sorted(self.items(), key=lambda item: item[1].__hash__())))

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

    def __lt__(self, other):
        return self.__hash__() < other.__hash__()

    def __gt__(self, other):
        return self.__hash__() > other.__hash__()


class HashableSet(set):
    def __init__(self, aset):
        """Initialize the HashableSet class.

        Args:
            aset (set): A set of elements to be added to the HashableSet.
                If an element is a dictionary, list, or set, it will be converted to a HashableDict,
                HashableList, or HashableSet respectively before being added to the HashableSet.

        Returns:
            None
        """

        content = set()
        for item in aset:
            if isinstance(item, dict):
                item = HashableDict(item)
            elif isinstance(item, list):
                item = HashableList(item)
            elif isinstance(item, set):
                item = HashableSet(item)
            content.add(item)
        super().__init__(content)

    def __hash__(self):
        """Return the hash value of the object by converting it to a frozenset."""

        return hash(frozenset(self))

    def __eq__(self, other):
        """Return True if the hash values of self and other are equal, False otherwise."""

        return self.__hash__() == other.__hash__()

    def __lt__(self, other):
        """Return True if self is less than other based on their hash values."""

        return self.__hash__() < other.__hash__()

    def __gt__(self, other):
        """Return True if the hash value of self is greater than the hash value of other, False otherwise."""

        return self.__hash__() > other.__hash__()


class StagedItem(dict):

    # stages must be a dict of keys with according integer values. Negative values are the defaults.
    # (not counted during the boolean check of the dict, but still returned with a call)
    stages: Dict[str, Any]
    # valid stages serves to indicate if one stage is there for keeping the data
    # (for visualizing what went bad for example), but should not be automatically used with latest or first.
    # valid_stages: List[bool]

    valid_stages: Dict[str, bool]

    def __init__(self, dico=None, **kwargs):
        """Initialize the object with a dictionary.

        Args:
            dico (dict, optional): The dictionary to initialize the object with. Defaults to an empty dictionary.
        """
        dico = {} if dico is None else dico
        dico.update(kwargs)
        super().__init__(self.sanitize(dico))
        #
        self.valid_stages = {k: True for k in self.stages.keys()}

    def sanitize(self, dico):
        """Sanitize the input dictionary by checking if all keys are allowed.

        Args:
            dico (dict): The input dictionary to be sanitized.

        Returns:
            dict: The sanitized dictionary.

        Raises:
            KeyError: If any key in the input dictionary is not allowed.

        Example:
            sanitize({"key1": value1, "key2": value2})
        """

        for key in dico.keys():
            if key not in self.stages.keys():
                raise KeyError(
                    f"Cannot put object {key} into this {self.__class__.__name__}. "
                    f"Only the keys : {', '.join(self.all_stages_keys)} are allowed"
                )
        return dico

    def add(self, valid=True, **kwargs):
        """Add a key-value pair to the dictionary after sanitizing the input.

        Args:
            key: The key to be added to the dictionary.
            value: The value corresponding to the key.

        Returns:
            None
        """
        kwargs = self.sanitize(kwargs)

        # if we try to set invalid stages, we must do one by one.
        if valid == False:
            if len(kwargs) > 1:
                raise ValueError(
                    "Cannot set several invalid stages at the same time with add. "
                    "You must instead call the function once per invalid stage set."
                )
            # else:
            # key = list(kwargs.keys())[0]
            # self.valid_stages[key] = False
            # stage_position = list(self.stages.keys()).index(key)
            # self.valid_stages[stage_position] = False

        self.update(kwargs)
        self.valid_stages.update({k: valid for k in kwargs.keys()})

    def set_validity(self, **kwargs: bool):
        for key, validity in kwargs.items():
            if key not in self.keys():
                if key not in self.stages.keys():
                    raise ValueError(f"{key} is not available in the {self.__class__.__name__}")
                raise ValueError(
                    f"Cannot set validity of {key} into this {self.__class__.__name__}. "
                    f"Only the keys : {', '.join(self.all_stages_keys)} are allowed"
                )
            # stage_position = list(self.stages.keys()).index(key)
            # self.valid_stages[stage_position] = bool(validity)
            self.valid_stages[key] = bool(validity)

    def __call__(self):
        return self.latest()

    def latest(self, offset=-1):
        """Return the latest stage data from the object (including defaults).

        Raises:
            ValueError: If the object is empty and cannot get the latest stage data.
        """
        offset = abs(offset) - 1

        for position, key in enumerate(reversed(self.filter_valid_keys(self.sorted_stages(self.all_stages_keys)))):
            if key in self.keys() and position >= offset:
                return self[key]
        else:
            raise ValueError(f"This {self.__class__.__name__} is empty ! Cannot get the latest stage data from it")

        raise ValueError("{self.__class__.__name__} don't contain enough items to get the last with offset -{offset}")

    def latest_key(self, offset=-1):
        offset = abs(offset) - 1

        for position, key in enumerate(reversed(self.filter_valid_keys(self.sorted_stages(self.all_stages_keys)))):
            if key in self.keys() and position >= offset:
                return key
        else:
            raise ValueError(f"This {self.__class__.__name__} is empty ! Cannot get the latest stage data from it")

        raise ValueError("{self.__class__.__name__} don't contain enough items to get the last with offset -{offset}")

    def first(self):
        """Return the first stage data from the object (including defaults).

        Raises:
            ValueError: If the object is empty and cannot get the latest stage data.
        """

        for key in self.filter_valid_keys(self.sorted_stages(self.all_stages_keys)):
            if key in self.keys():
                return self[key]
        raise ValueError(f"This {self.__class__.__name__} is empty ! Cannot get the latest stage data from it")

    @property
    def non_default_keys(self):
        return [name for name, key in self.stages.items() if key >= 0]

    @property
    def default_keys(self):
        return [name for name, key in self.stages.items() if key < 0]

    @property
    def all_stages_keys(self):
        return list(self.stages.keys())

    def sorted_stages(self, keys):
        """Return a list of stage names sorted by their values."""
        return sorted(keys, key=lambda x: self.stages[x])

    def filter_valid_keys(self, keys: list[str]):
        return [
            key for key in keys if self.valid_stages[key]
        ]  # self.valid_stages[list(self.stages.keys()).index(key)]]

    def __bool__(self):
        filtered_keys = self.filter_valid_keys(self.non_default_keys)
        return bool(len({key: value for key, value in self.items() if key in filtered_keys}))

    def __getstate__(self):
        """Return the state to be pickled, excluding the 'stages' attribute."""
        state = self.__dict__.copy()
        state.pop("stages", None)  # Remove 'stages' from the state
        return state

    def __setstate__(self, state):
        """Restore the state from the pickle, re-initializing 'stages'."""
        self.__dict__.update(state)
        self.stages = type(self).stages  # Re-initialize 'stages'

        reloaded_valid_stages = self.valid_stages.copy()

        patched_valid_stages = {k: True for k in self.stages.keys()}

        if isinstance(reloaded_valid_stages, list):
            # make it a list expeting the new items to be added at the end if there is some.
            reloaded_valid_stages = {k: bool(v) for k, v in zip(self.stages.keys(), reloaded_valid_stages)}

        patched_valid_stages.update(reloaded_valid_stages)
        self.valid_stages = patched_valid_stages
