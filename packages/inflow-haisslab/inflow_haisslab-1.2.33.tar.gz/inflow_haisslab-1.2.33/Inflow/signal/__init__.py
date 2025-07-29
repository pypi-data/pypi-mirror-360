# -*- coding: utf-8 -*-
"""
Created on Wed Jan 11 19:48:55 2023

@author: tjostmou
"""

from . import fluo  # todo : replace fluo by norm
from . import norms
from . import filters
from . import fits
from . import resample


def get_splices(List, threshold=None, comparison=">="):

    # Supports Nan containing arrys and is in fact, in part, written to handle
    # detection of edges between numeral data and nan chunks in time series

    import numpy as np
    from operator import lt, le, eq, gt, ge, ne

    operators = {"<": lt, "<=": le, "=": eq, ">": gt, ">=": ge, "!=": ne}

    comparison = operators[comparison]

    _List = np.asarray(List.copy())

    if threshold is not None:
        if np.isnan(threshold):
            for idx, val in enumerate(_List):
                if not np.isnan(val):
                    _List[idx] = 1
        else:
            for idx, val in enumerate(_List):
                if np.isnan(val):
                    continue
                if comparison(val, threshold):
                    _List[idx] = 1
                else:
                    _List[idx] = 0

    ranges = [
        i + 1
        for i in range(len(_List[1:]))
        if not ((_List[i] == _List[i + 1]) or (np.isnan(_List[i]) and np.isnan(_List[i + 1])))
    ]
    ranges.append(len(_List))
    ranges.insert(0, 0)

    slices = []
    values = []
    for i in range(len(ranges) - 1):
        slices.append([ranges[i], ranges[i + 1]])
        if _List[ranges[i]] is None:
            values.append(None)
        else:
            values.append(_List[ranges[i]])

    return slices, values


def get_splices_indices(array, threshold=None, comparison=">=", edge="first"):
    slices, values = get_splices(array, threshold, comparison)
    if edge == "first":
        edges = [0]
    elif edge == "last":
        edges = [1]
    else:
        edges = [0, 1]

    edges_indices = [
        edge
        for event, above_threshold in zip(slices, values)
        for edge_num, edge in enumerate(event)
        if above_threshold and edge_num in edges
    ]
    return edges_indices
