# -*- coding: utf-8 -*-

import re, os


def relative_path(absolute_path, common_root_path):
    """
    Compare an input path and a path with a common root with the input path, and returns only the part of the input path that is not shared with the _common_root_path.

    Args:
        input_path (TYPE): DESCRIPTION.
        common_root_base (TYPE): DESCRIPTION.

    Returns:
        TYPE: DESCRIPTION.

    """
    absolute_path = os.path.normpath(absolute_path)
    common_root_path = os.path.normpath(common_root_path)
    
    commonprefix = os.path.commonprefix([common_root_path,absolute_path])
    if commonprefix == '':
        raise IOError(f"These two pathes have no common root path : {absolute_path} and {common_root_path}")
    return os.path.relpath(absolute_path, start = commonprefix )

def component(pattern , path):
    return qregexp(pattern, path, groupidx = 0)
    

def qregexp(regex, input_line, groupidx=None, matchid=None , case=False):
    """
    Simplified implementation for matching regular expressions. Utility for python's built_in module re .

    Tip:
        Design your patterns easily at [Regex101](https://regex101.com/)

    Args:
        input_line (str): Source on wich the pattern will be searched.
        regex (str): Regex pattern to match on the source.
        **kwargs (optional):
            - groupidx : (``int``)
                group index in case there is groups. Defaults to None (first group returned)
            - matchid : (``int``)
                match index in case there is multiple matchs. Defaults to None (first match returned)
            - case : (``bool``)
                `False` / `True` : case sensitive regexp matching (default ``False``)

    Returns:
        Bool , str: False or string containing matched content.

    Warning:
        This function returns only one group/match.

    """

    if case :
        matches = re.finditer(regex, input_line, re.MULTILINE|re.IGNORECASE)
    else :
        matches = re.finditer(regex, input_line, re.MULTILINE)

    if matchid is not None :
        matchid = matchid +1

    for matchnum, match in enumerate(matches,  start = 1):

        if matchid is not None :
            if matchnum == matchid :
                if groupidx is not None :
                    for groupx, groupcontent in enumerate(match.groups()):
                        if groupx == groupidx :
                            return groupcontent
                    return False

                else :
                    MATCH = match.group()
                    return MATCH

        else :
            if groupidx is not None :
                for groupx, groupcontent in enumerate(match.groups()):
                    if groupx == groupidx :
                        return groupcontent
                return False
            else :
                MATCH = match.group()
                return MATCH
    return False