# -*- coding: utf-8 -*-
"""
Created on Fri Feb  3 22:22:33 2023

@author: tjostmou
"""


from logging import getLogger
from ..core.decorators import hide_unused_kwargs
from ..core.special_types import AttrDict
from .helpers import (
    get_preprocessed_filename,
    get_suite2p_path,
)
import numpy as np, pandas as pd, pickle, os
from ..tdms.content import Reader as tdms, read as tdms_content
from ..tiff.content import Reader as tiff, read as tiff_content
from ..core.utils import return_module
from functools import wraps
import re, json

from typing import Literal


def preprocessed_data(session_details, alf_identifier, extra=""):
    local_log = getLogger()
    filename = get_preprocessed_filename(session_details, alf_identifier, extra)
    try:
        with open(filename, "rb") as f:
            r = pickle.load(f)

            local_log.debug(f"Loaded file {filename}{'.' + extra if extra else ''}")
            return r
    except FileNotFoundError as e:
        raise IOError(f"The file {filename} that has been tried to be read do not exist")
    except ModuleNotFoundError as e:
        local_log.debug(f"Unable to load {filename}{'.' + extra if extra else ''} using generick pickling")
        if "pandas" in e.__str__():
            local_log.debug("Trying out pandas read_pickle")
            import pandas as pd

            r = pd.read_pickle(filename)
            return r
        else:
            local_log.debug(f"Pandas not found in {e.__str__()}. Raising error")
            raise e


def suite2p_metadata(session_details, collection="", plane: int | str = 0):
    suite2p_results_paths = get_suite2p_path(session_details, collection, plane)

    filename = "ops.npy"

    try:
        object_path = [item for item in suite2p_results_paths if filename in item][0]
    except IndexError:  # no file has been found
        raise IOError(
            "No ops.npy file have been found with specified location"
            f" {session_details.path}{'/' + collection if collection else ''}/plane{plane}"
        )

    return npy_file(object_path).item()


@hide_unused_kwargs
def suite2p_files(
    session_details,
    collection="",
    plane: int | str = 0,
    stat: Literal["most_recent", "original"] = "most_recent",
    **unused_kwargs,
):
    def get_var_filename(files, var):
        filename = var + ".npy"
        object_path = [item for item in files if filename in item]
        if len(object_path):
            return object_path[0]
        # else : no file found correspunding to that variable
        return None

    # absolute paths of all numpy files at the root of the suite2p/planeN folder for that session
    suite2p_results_files = get_suite2p_path(session_details, collection, plane)

    loadable_vars = ["F", "iscell", "redcell", "spks"]
    non_timing_patterns = ["ops", "stat"]

    if stat == "most_recent":
        stat_var = "stat"
    elif stat == "original":
        stat_var = "stat_orig"
    else:
        raise ValueError("stat value must either be 'most_recent' or 'original'")

    stat_path = get_var_filename(suite2p_results_files, stat_var)
    if stat_path is None:
        raise IOError(
            f"The file {stat_var}.npy must exist in the folder"
            f" {session_details.path}{'/' + collection if collection else ''}/plane{plane}, which is not be the case."
            " Cannot generate results dataframe"
        )

    cells_df = pd.DataFrame(npy_file(stat_path).tolist())

    for var_path in suite2p_results_files:
        # we skip the iteration if the nupy file is one of the non_timing_patterns
        if any([pattern in var_path for pattern in non_timing_patterns]):
            continue

        # get the basename without extension
        varname = os.path.splitext(os.path.basename(var_path))[0]

        # we also skip if the stem of the file is not starting with one of loadable_vars possibilities
        if not any([varname.startswith(pattern) for pattern in loadable_vars]):
            continue

        object_content = npy_file(var_path)
        cells_df.loc[:, varname] = object_content.tolist()

    return cells_df.reset_index().rename(columns={"index": "roi#"}).set_index("roi#")


def suite2p_binary(session_details, chan=""):
    try:
        from suite2p.io.binary import BinaryRWFile
    except ImportError:
        from suite2p.io.binary import BinaryFile as BinaryRWFile

    # if reading channel 2, set chan = "_chan2"
    meta = suite2p_metadata(session_details=session_details)
    reader = BinaryRWFile(
        meta["Ly"],
        meta["Lx"],
        get_suite2p_path(session_details, file=rf"data{chan}\.bin")[0],
    )
    return reader
    # from this reader you can use .data to get all data or .read()
    # to get frames one by one or .ix([1,2,3]) to get frames 1,2,3 for example.


def mask(session_details, alf_identifier, extra=None, collection=""):
    """
    Loads a mask file in the same way than it was saved with Inflow.save.mask() function.

    Parameters
    ----------
    session_details : pd.series or AttrDict (contains session  infos)
        This is used to get access to the session folder to save the mask (by default on the root of the session).
    alf_identifier : str
        alf (for alyx filename) identifier is a string that gives info about what is the content of the mask you saved.
        It is used to reconstruct the file name.
        ( An example finished filename by this function will be
        as follow : `[session_details.path]/[collection]/mask.[alf_identifier].bmp`).
    extra : str, optional
        If you specified subcategorical informations to your mask content.
        For example :
            Using alf_identifier = "barrel"
            and
            extra = "C1" or "D1" :
            The resulting filename will be : `.../mask.barrels.C1.bmp` or `.../mask.barrels.D1.bmp`
        The default is None.
    collection : str, optional
        The subfolder(s) (inside the session_details.path) where you saved the mask into. The default is "".
        If wou saved it into nested (multiple) subfolders, you can specify : collection = "masks/whiskers" for example.

    Raises
    ------
    IOError
        In case the file exists but the content could not be loaded.

    Returns
    -------
    mask : numpy 2D array or None if the file do not exist (throws a warning in the log stream if it's the case)
    """
    from one.alf.spec import to_alf
    import cv2, os

    local_log = getLogger()

    filename = to_alf(
        "mask",
        alf_identifier,
        extension="bmp",
        namespace=None,
        timescale=None,
        extra=extra,
    )

    filepath = os.path.join(session_details.path, collection, filename)

    if os.path.isfile(filepath):
        try:
            mask = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE).astype(bool)
            local_log.load(f"Loaded mask {alf_identifier}.{extra}")
            return mask
        except AttributeError:
            raise IOError(f"Unable to extract mask from path {filepath}. Make sure there is no spaces in the path !!!")
    else:
        local_log.warning(f"Mask at path: {filepath} does not exist")

    return None


def npy_file(filepath):
    return np.load(filepath, allow_pickle=True)


def mat_file(filepath):
    def _recursively_add_key(result_dic, intput_dic, upper_key=None, upmost_object=None):
        downward_result = result_dic if upper_key is None else result_dic[upper_key]
        upmost_object = intput_dic if upmost_object is None else upmost_object

        try:
            for key, sub_inout_dict in intput_dic.items():
                if (
                    key == "#refs#"
                ):  # refs# fiels are metadata related to the way data is stored inside the hdf5/mat file.
                    continue  # We don't care about them
                downward_result[key] = {}  # create an empty dict that we pass down, because "we need to go deeper".
                _recursively_add_key(downward_result, sub_inout_dict, key, upmost_object)

        except AttributeError:  # intput_dic has no keys. Use it as an array instead.
            if intput_dic.dtype == "object":
                reference = intput_dic[0][0]
                result_dic[upper_key] = np.array(upmost_object[reference])

            else:
                result_dic[upper_key] = np.array(intput_dic[0], dtype=intput_dic.dtype)

            try:  # try to convert to scalar if relevant, to avoid lonely scalar nested in arrays
                result_dic[upper_key] = result_dic[upper_key].item()
            except ValueError:  # if this is raised, not relevant
                pass

    from scipy.io import loadmat

    try:
        return loadmat(filepath)
    except NotImplementedError:
        from h5py import File

        result = {}
        with File(filepath, "r") as filehandle:
            _recursively_add_key(result, filehandle)
        return result


def commented_json_file(json_file):
    with open(json_file, "r") as file:
        json_string = file.read()
    pattern = r"//[^\n{}]+"
    json_no_comments = re.sub(pattern, "", json_string, flags=re.DOTALL)
    return json.loads(json_no_comments)


def pipelines_arguments(session_details):
    path = os.path.join(session_details.path, "pipelines_arguments.json")
    return commented_json_file(path)


def pipeline_function_arguments(session_details, function):
    local_log = getLogger()

    if callable(function):
        function = function.__name__

    try:
        all_args = pipelines_arguments(session_details)
    except FileNotFoundError:
        local_log.warning(
            f"Could not find the pipelines_arguments.json file for the session {session_details.alias}, skipping"
        )
        return {}
    except AttributeError:
        local_log.warning("The provided session_details don't have a path attribute. Please double check. Skipping")
        return {}

    try:
        alias = return_module(f"ResearchProjects.{all_args['project']}.aliases")
        locals().update({all_args["project"]: return_module(f"ResearchProjects.{all_args['project']}")})
    except KeyError:
        local_log.warning(
            f"pipelines_arguments.json file at {session_details.path} didn't contain any `project` key. Could not"
            " run imports, passing."
        )
        pass
    except ModuleNotFoundError:
        local_log.warning(f"Could not import ResearchProject.{all_args['project']}, passing.")
        pass

    try:
        all_args["functions"][function]
    except KeyError:
        local_log.warning(
            f"In pipelines_arguments.json file at {session_details.path} : Could not find the `functions` key or"
            f" the key `{function}`. Skipping"
        )
        return {}
    args = {}

    for key, value in all_args["functions"][function].items():
        if isinstance(value, str) and value.startswith("$"):
            try:
                value = eval(value[1:])
            except Exception as e:
                local_log.warning(
                    f"Could not evaluate expression : {value} for argument {key} in function {function}. Error :"
                    f" {type(e).__name__} : {e}. Passing"
                )
                continue
        args[key] = value
    return args
