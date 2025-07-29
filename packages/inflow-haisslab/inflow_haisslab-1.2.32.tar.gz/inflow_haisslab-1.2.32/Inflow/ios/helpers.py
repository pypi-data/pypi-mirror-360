# -*- coding: utf-8 -*-
"""
Created on Fri Feb  3 22:23:43 2023

@author: tjostmou
"""

from ..path.extract import relative_path
from ..core.decorators import session_to_path_argument
from ..path.find import files as findfiles
from ..core.logging import get_local_logger
import os
import pandas as pd


def get_suite2p_path(session_details, collection="suite2p", plane: int | str = 0, file=r".*\.npy$"):
    # collection allow to force finding only in a give subfolder of the session_path
    if not isinstance(collection, (tuple, list)):
        collection = [collection]
    try:
        return findfiles(os.path.join(session_details.path, *collection, f"plane{plane}"), re_pattern=file, levels=0)
    except FileNotFoundError:
        return []


def get_preprocessed_filename(
    session_details, alf_identifier, extra="", collection="preprocessing_saves", makedirs=False
):
    if extra is None or extra == "":
        extra = ()
    elif isinstance(extra, str):
        extra = extra.split(".")
    saved_preprocess_root = os.path.normpath(os.path.join(session_details.path, collection))
    extra = "." + "".join([ext + "." for ext in extra])
    filename = os.path.join(saved_preprocess_root, f"preproc_data.{alf_identifier}{extra}pickle")
    if makedirs and not os.path.isdir(saved_preprocess_root):
        os.makedirs(saved_preprocess_root)
    return filename


def cast_preprocessed_file_to_revision(session_details, alf_identifier, extra=None, collections="preprocessing_saves"):
    logger = get_local_logger()
    filename = get_preprocessed_filename(session_details, alf_identifier, extra=extra, collections=collections)
    if os.path.isfile(filename):
        import datetime

        revision = datetime.datetime.now().strftime("#revision-%Y-%m-%d#")
        revision = os.path.join(os.path.dirname(filename), revision)
        if not os.path.isdir(revision):
            os.makedirs(revision)
        new_file_name = os.path.join(revision, os.path.basename(filename))
        logger.debug(f"Original revised file path : {filename}")
        logger.debug(f"Newly revised file path : {new_file_name}")
        os.rename(filename, new_file_name)
    else:
        raise OSError(f"File {filename} does not exist, cannot cast file to revision")
