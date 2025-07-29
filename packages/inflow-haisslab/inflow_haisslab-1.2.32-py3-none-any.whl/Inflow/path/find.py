# -*- coding: utf-8 -*-
"""
Created on Mon Dec 12 19:23:16 2022

@author: tjostmou
"""

import os
import natsort
from . import extract

def files(input_path, re_pattern = None, relative = False,levels = -1, get = "files", parts = "all", sort = True):
    """
    Get full path of files from all folders under the ``input_path`` (including itself).
    Can return specific files with optionnal conditions 
    Args:
        input_path (str): A valid path to a folder. 
            This folder is used as the root to return files found 
            (possible condition selection by giving to re_callback a function taking a regexp pattern and a string as argument, an returning a boolean).
    Returns:
        list: List of the file fullpaths found under ``input_path`` folder and subfolders.
    """
    #if levels = -1, we get  everything whatever the depth (at least up to 32767 subfolders, but this should be fine...)

    if levels == -1 :
        levels = 32767
    current_level = 0
    output_list = []
    
    def _recursive_search(_input_path):
        nonlocal current_level
        for subdir in os.listdir(_input_path):
            fullpath = os.path.join(_input_path,subdir)
            if os.path.isfile(fullpath): 
                if (get == "all" or get == "files") and (re_pattern is None or extract.qregexp(re_pattern,fullpath)):
                    output_list.append(os.path.normpath(fullpath))
                    
            else :
                if (get == "all" or get == "dirs" or get == "folders") and (re_pattern is None or extract.qregexp(re_pattern,fullpath)):
                    output_list.append(os.path.normpath(fullpath))
                if current_level < levels:
                    current_level += 1 
                    _recursive_search(fullpath)
        current_level -= 1
        
    if os.path.isfile(input_path):
        raise ValueError(f"Can only list files in a directory. A file was given : {input_path}")
 
    _recursive_search(input_path)
    
    if relative :
        output_list = [os.path.relpath(file,start = input_path) for file in output_list]
    if parts == "name" :
        output_list = [os.path.basename(file) for file in output_list]
    if sort :
        output_list = natsort.natsorted(output_list)
    return output_list
        

    
        