# -*- coding: utf-8 -*-
"""
Created on Mon Dec 12 19:24:24 2022

@author: tjostmou
"""

import os, re
from IPython.display import display
import pandas as pd, numpy as np
from . import pattern
from . import extract
from ..core.decorators import recurse
from ..core.logging import get_local_logger
from .find import files as find_files


def auto_rename_session_files_to_alf(selected_folder, dry_run=True, return_tables=False):
    """Renames session files to ALF format.

    Args:
        selected_folder (str): The path to the folder containing the files to be renamed.
        dry_run (bool, optional): If True, only display the changes without applying them. Defaults to True.

    Returns:
        pd.dataframe: A dataframe containing the new file names after renaming in the column 'new_pathes',
        in from of the original file names in the column 'origin_pathes'.
    """
    logger = get_local_logger()

    origin_pathes = find_files(
        selected_folder, relative=False, levels=-1, get="files"
    )  # , re_pattern = '(?:.*\.tif.*)|(?:.*\.tdms)')
    new_pathes = path_to_alf(origin_pathes, force=True)
    conflicts, new_pathes = check_file_rename_conflicts(origin_pathes, new_pathes)
    returns = {}
    if len(conflicts):
        with pd.option_context(
            "display.max_rows",
            500,
            "display.max_columns",
            500,
            "display.width",
            1000,
            "expand_frame_repr",
            False,
            "max_colwidth",
            None,
        ):
            logger.error("Some conflicts exist with file renamings. Cannot proceed. Please check below")
            display(conflicts)
    if return_tables:
        returns["conflicts_df"] = conflicts
    names_after_renaming = apply_name_change(origin_pathes, new_pathes, dry_run=dry_run)

    comparison_df = pd.DataFrame(np.array([origin_pathes, new_pathes]).T, columns=["origin_pathes", "new_pathes"])
    if comparison_df["new_pathes"].apply(lambda cell: cell == "" or cell == "NOT_INCLUDED").all():
        logger.info("All files supplied are already correctly renamed according to format rules. Passing")
    else:
        logger.info("You can look the table below to check if files renaming seems to be ok.")
        with pd.option_context(
            "display.max_rows",
            500,
            "display.max_columns",
            500,
            "display.width",
            1000,
            "expand_frame_repr",
            False,
            "max_colwidth",
            None,
        ):
            display(comparison_df)

    if return_tables:
        returns["comparison_df"] = comparison_df
        returns["names_after_renaming"] = names_after_renaming

    return returns if return_tables else names_after_renaming


def check_file_rename_conflicts(src_list, new_list):
    conflicts = []
    fixed_new_files = []
    for src_file, new_file in zip(src_list, new_list):
        if new_file in ["AUTO-DELETE", "NOT_INCLUDED"]:
            fixed_new_files.append(new_file)
            continue
        elif src_file == new_file or new_file == "" or new_file == "INCLUDED_WITHOUT_CHANGE":
            fixed_new_files.append("INCLUDED_WITHOUT_CHANGE")
        elif os.path.isfile(new_file):
            fixed_new_files.append("CONFLICTED_DUPLICATE")
            conflicts.append({"source": src_file, "new_name_conflicted": new_file})
        else:
            fixed_new_files.append(new_file)
    return pd.DataFrame(conflicts), fixed_new_files


def apply_name_change(src_list, new_list, dry_run=True):
    """Renames files in the src_list to the corresponding names in the new_list.

    Args:
        src_list (list): A list of source file paths to be renamed.
        new_list (list): A list of new file paths to rename the source files to.
        dry_run (bool, optional): If True, only display the changes without applying them. Defaults to True.

    Returns:
        list: A list containing the new file names after renaming.
    """
    if not len(src_list) == len(new_list):
        raise ValueError("Length of lists must match for name conversion")
    if "CONFLICTED_DUPLICATE" in new_list:
        raise IOError("Some files are conflicted, cannot apply any renaming to prevent errors")

    logger = get_local_logger()

    if dry_run:
        logger.warning(
            "The apply_name_change function was called with option dry_run = True. It will only show you what files it would have renamed, without actually renaming them."
        )
        logger.warning("If things look ok, you can set it to False to actually do the process.")

    names_after_renaming = []
    for src_file, new_file in zip(src_list, new_list):
        if new_file == "" or new_file == "INCLUDED_WITHOUT_CHANGE":
            names_after_renaming.append(src_file)
            continue
        if new_file == "AUTO-DELETE":
            if not dry_run:
                os.remove(src_file)
            continue
        if (
            new_file == "NOT_INCLUDED"
        ):  # will not be returned, so will not be used for file registration, but not deleted either
            continue
        if not dry_run:
            os.rename(src_file, new_file)
        names_after_renaming.append(new_file)
    return names_after_renaming


def append_extra(new_extra, extra=None):
    if new_extra is None:
        return extra
    return extra + "." + new_extra


def extract_extra_from_non_alfpath(filename, re_pattern):
    results = []
    matches = re.finditer(re_pattern, filename, re.MULTILINE | re.IGNORECASE)

    for matchnum, match in enumerate(matches, start=1):
        for groupx, groupmatch in enumerate(match.groups()):
            results.append(groupmatch)
    return results


def file_to_alf(filename, alf_info):
    import one

    def _finish_file():
        return one.alf.spec.to_full_path(**alf_info)

    def get_imaging_type(collec):
        imaging_types = ("pupil",)

        for i_type in imaging_types:
            if i_type in collec:
                return i_type
        return None

    if alf_info["extension"] == "tif" or alf_info["extension"] == "tiff":
        alf_info["object"] = "imaging"

        if alf_info["collection"] is not None:
            if "imaging_data" in alf_info["collection"]:
                trial_no = extract_extra_from_non_alfpath(filename, pattern.TIFF_FRAME_NO)

                if trial_no:
                    alf_info["extra"] = trial_no[0].zfill(5)
                    alf_info["attribute"] = "frames"
                    return _finish_file()

        else:
            return "NOT_INCLUDED"

    elif alf_info["extension"] == "tdms":

        if alf_info["collection"] is None or alf_info["collection"] == "":
            alf_info["object"] = "trials"
            alf_info["attribute"] = "eventTimeline"
            return _finish_file()

        elif "behaviour_imaging" in alf_info["collection"]:
            alf_info["object"] = "behaviour"
            alf_info["attribute"] = "video"
            i_type = get_imaging_type(alf_info["collection"])

            if i_type is not None:
                alf_info["extra"] = i_type
                trial_no = extract_extra_from_non_alfpath(filename, pattern.TDMS_VIDEO_TRIAL_NO)

                if trial_no:
                    alf_info["extra"] = append_extra(trial_no[0].zfill(5), alf_info["extra"])
                    return _finish_file()

        elif "intrinsic_optical_imaging" in alf_info["collection"]:
            if alf_info["object"] == "imaging_intrinsic":
                return ""
            alf_info["collection"] = "intrinsic_optical_imaging"
            whisker = extract_extra_from_non_alfpath(alf_info["object"], pattern.IOI_WHISKER)
            alf_info["object"] = "imaging_intrinsic"
            alf_info["attribute"] = "delta_stim_images"
            if whisker:
                alf_info["extra"] = whisker[0]
            return _finish_file()

    elif alf_info["extension"] == "PNG" or alf_info["extension"] == "png":
        alf_info["extension"] = "png"  # enforce lower caps
        if alf_info["collection"] is not None and "imaging_data" in alf_info["collection"]:
            FOV_no = extract_extra_from_non_alfpath(filename, pattern.FOV_NO)

            if FOV_no:
                alf_info["object"] = "imaging"
                alf_info["attribute"] = "fieldOfView"
                alf_info["extra"] = FOV_no[0].zfill(2)
                return _finish_file()
        else:
            return "NOT_INCLUDED"

    elif alf_info["extension"] == "SVG" or alf_info["extension"] == "svg":
        return "NOT_INCLUDED"

    elif alf_info["extension"] is None:
        if "intrinsic_optical_imaging" in alf_info["collection"]:
            alf_info["collection"] = "intrinsic_optical_imaging"
            if alf_info["object"] is None:
                return "NOT_INCLUDED"
            if "reference" in alf_info["object"]:
                alf_info["object"] = "imaging_intrinsic"
                alf_info["attribute"] = "vessels_reference"
                alf_info["extension"] = "tiff"
                return _finish_file()
            else:
                whisker = extract_extra_from_non_alfpath(alf_info["object"], pattern.IOI_WHISKER)
                alf_info["object"] = "imaging_intrinsic"
                alf_info["attribute"] = "bin_delta_stim_images"
                alf_info["extension"] = "binlv"
                if whisker:
                    alf_info["extra"] = whisker[0]
                return _finish_file()

    elif alf_info["extension"] == "tdms_index":
        return "AUTO-DELETE"

    elif alf_info["extension"] == "db":
        if alf_info["object"] == "Thumbs":
            return "NOT_INCLUDED"

    return "NOT_INCLUDED"  # if none of the renaming directives returned a results above, we don't rename, and don't include in registered files


@recurse
def path_to_alf(filepath, force=False):
    import one

    session_path = one.alf.files.get_session_path(filepath)
    if session_path is None:
        raise ValueError(
            f"The path is not a valid path of a session. Make sure you have a path matching : {one.alf.spec.path_pattern()}"
        )

    # filename = os.path.split(filepath)[1]
    # alf_info = one.alf.files.full_path_parts( filepath , as_dict = True, assert_valid = False)
    # alf_info["extension"] = os.path.splitext(filepath)[1][1:] # this will work even if extension is ''

    alf_info = one.alf.files.full_path_parts(filepath, as_dict=True, absolute=True, assert_valid=False)

    if not force and one.alf.spec.is_valid(filepath, one.alf.spec.FULL_ABSOLUTE_SPEC):
        return (
            ""  # no file name change. We do not return None to stay compatible with string type columns of dataframes
        )

    new_path = file_to_alf(filepath, alf_info)
    if new_path is None:
        return ""

    # new_path = os.path.normpath(os.path.join(session_path,new_filename) if alf_info["collection"] is None else os.path.join(session_path,alf_info["collection"],new_filename))

    # if new_path == filepath :
    #    return ''
    return new_path


def make_homogeneous_empty_dataset_from_filelist(files, session_id, repository_name, dry_run=True):
    import one

    cnx = one.api.ONE()

    logger = get_local_logger()

    # repo_path = cnx.get_data_repository_path(repository_name)
    session_eid = cnx.to_eid(session_id)
    if session_eid is None:
        raise ValueError(f"The session {cnx.path2ref(session_id, as_dict = False)} doesn't seem to exist")
    session_details = cnx.to_session_details(
        cnx.alyx.rest("sessions", "read", session_eid, no_cache=True), as_mode="remote"
    )

    # Verify all goes well for a batch of alf file
    common_alf_type = {}
    for file in files:
        # alf_name = os.path.relpath(file, start = os.path.relpath(session_details["path"], start = repo_path))

        # new version :
        logger.debug(f"file path is : {file}")
        try:
            parts = one.alf.files.full_path_parts(file, as_dict=True, absolute=True)
            for key in ["root", "lab", "subject", "date", "number"]:
                parts.pop(key, None)
        except ValueError:
            parts = one.alf.files.full_path_parts(file, as_dict=True, absolute=False)
            for key in ["root", "lab", "subject", "date", "number"]:
                parts.pop(key, None)

        alf_name = one.alf.spec.to_full_path(**parts, dromedarize=False)

        if len(common_alf_type):
            alf_type = one.alf.files.rel_path_parts(alf_name.replace("\\", "/"), as_dict=True)
            logger.debug(f"file parts are : {alf_type}")

            if alf_type["collection"] != common_alf_type["collection"]:
                raise ValueError(
                    "Registering several files under a same dataset require them being under the same collection (session subdirectory)"
                )
            if alf_type["revision"] != common_alf_type["revision"]:
                raise NotImplementedError
            if alf_type["object"] != common_alf_type["object"]:
                raise ValueError(
                    "Registering several files under a same dataset require them having the same object name (first name before dot)"
                )
            if alf_type["attribute"] != common_alf_type["attribute"]:
                raise ValueError(
                    "Registering several files under a same dataset require them having the same attribute name (second name before dot)"
                )
            if alf_type["extension"] != common_alf_type["extension"]:
                raise ValueError(
                    "Registering several files under a same dataset require them having the same extension (second name before dot)"
                )
        else:
            common_alf_type = one.alf.files.rel_path_parts(alf_name.replace("\\", "/"), as_dict=True)

    if common_alf_type["collection"] is None:
        common_alf_type["collection"] = ""

    d = {
        "created_by": one.params.get().ALYX_LOGIN,
        "dataset_type": common_alf_type["object"] + "." + common_alf_type["attribute"],
        "data_format": "." + common_alf_type["extension"],
        "collection": common_alf_type["collection"],
        "session_pk": session_details.name,
        "data_repository": repository_name,
    }

    non_accepted_matching_keys = ["dataset_type", "collection"]
    for existing_dataset in session_details["data_dataset_session_related"]:
        # print(existing_dataset)
        booleans = [existing_dataset[key] == d[key] for key in non_accepted_matching_keys]
        logger.debug("checking existing dataset : " + str(existing_dataset))
        if all(booleans) == True:  # all keys are matching, the dataset already exists, returning it.
            logger.info(
                f"The dataset {d['collection']} - {d['dataset_type']} was already existing. Using it to attach files instead of creating a new one."
            )
            return existing_dataset

    # if it doesn't exist, create it
    logger.info(f"Registering dataset : {d}")
    if not dry_run:
        new_dataset = cnx.alyx.rest("datasets", "create", data=d)
    else:
        new_dataset = None

    return new_dataset


def add_files_to_empty_homogeneous_dataset(files, dataset_dict, dry_run=True):
    import one

    cnx = one.api.ONE()
    logger = get_local_logger()

    check_files = False
    if dataset_dict is None:
        if not dry_run:
            raise ValueError(
                "The dataset_dict returned by make_homogeneous_empty_dataset_from_filelist before calling add_files_to_empty_homogeneous_dataset seemed to be None, and dry run was not set to True. Cannot proceed."
            )

    else:
        logger.debug("dataset_dict : " + str(dataset_dict))
        try:
            existing_files = cnx.alyx.rest("datasets", "read", dataset_dict["id"], no_cache=True)["file_records"]
            check_files = True
        except KeyError:
            pass

    for file in files:
        file = file.replace("\\", "/")

        file_already_existing = False

        if check_files:
            for ex_file in existing_files:
                if file == ex_file["relative_path"]:
                    logger.error(f"File {file} already exist in dataset, it was not added")
                    file_already_existing = True
                    break

        parts = one.alf.files.full_path_parts(file, as_dict=True, absolute=False)

        if not file_already_existing:
            d = {
                "dataset": dataset_dict["id"] if dataset_dict is not None else "",
                "extra": parts["extra"] if parts["extra"] is not None else "",
                "exists": True,
            }
            logger.info(f"Registering file : {d}")
            if not dry_run:
                new_file_record = cnx.alyx.rest("files", "create", data=d)


def register_files(file_list, session_id, repository_name=None, dry_run=True):
    # TODO : eventually can change the function to use repository_name based on the root of the provided session_path (now session_id)
    # This would limit the amount of info the use have to enter, and also tell the user that he cannot put data there if the repository doesn't exist.
    # ideally i could go even further and only use the files path in file list to get session and repository...
    logger = get_local_logger()

    if not len(file_list):
        logger.warning("No file to register in file_list, passing.")
        return

    if repository_name is None:
        roots = set()
        cnx = one.api.ONE()
        for file in file_list:
            path_parts = one.alf.files.session_path_parts(file, as_dict=True, absolute=True)
            roots.add(path_parts["root"])
        if len(roots) > 1:
            raise ValueError(
                "More than one data repository was found for the files given. The function cannot register files to more tha one session at once. Please change the file_list input."
            )

        root = os.path.normpath(list(roots)[0])
        found = False
        for repo in cnx.alyx.rest("data-repository", "list", no_cache=True):
            value = os.path.normpath(repo["data_path"])
            if value == root:
                repository_name = repo["name"]
                found = True
                logger.info(
                    f"Found a common data-repository in the filepaths to use for registering : {repository_name}"
                )
                break
        if not found:
            raise ValueError(
                "No existing data repository was found for the location of the files you are trying to register. Either check their location and move them, or add a new data repository"
            )

    if dry_run:
        logger.warning(
            "The register_files function was called with option dry_run = True. It will only show you what files it would have registered, without actually registering them."
        )
        logger.warning("If things look ok, you can set it to False to actually do the process.")

    results = [
        one.alf.files.full_path_parts(file, as_dict=True, assert_valid=False, absolute=True) for file in file_list
    ]
    fileparts_df = pd.DataFrame(results)

    for collection_name, collection_selection in fileparts_df.groupby("collection", dropna=False):
        for filenames, files_collections in collection_selection.groupby(["object", "attribute"], dropna=False):
            if files_collections.isna().all().all():
                continue  # if file is realy not supporting the ALF standard, we won't be able to recompose it with one.alf.spec.to_full_path, so we won't include it in addible datasets anyway
            if files_collections.iloc[0]["collection"] == "preprocessing_saves":
                continue
            if files_collections.iloc[0]["collection"] == "figures":
                continue

            display(files_collections)
            files = files_collections.apply(lambda row: one.alf.spec.to_full_path(**row), axis=1).tolist()
            bools = [os.path.isfile(file) for file in files]
            root_path = files_collections.iloc[0]["root"]
            if sum(bools) == len(bools):  # all files have been reconstitued correctly and correspond to existing files
                files = [os.path.relpath(file, start=root_path) for file in files]

                new_dataset = make_homogeneous_empty_dataset_from_filelist(
                    files, session_id, repository_name, dry_run=dry_run
                )
                add_files_to_empty_homogeneous_dataset(files, new_dataset, dry_run=dry_run)


# use one.alf.files.session_path_parts(selected_folder,as_dict = True,absolute = True)
