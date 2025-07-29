# -*- coding: utf-8 -*-
"""
Created on Fri Feb  3 22:22:53 2023

@author: tjostmou
"""
from ..core.logging import get_local_logger
from ..path.extract import relative_path
from .helpers import get_preprocessed_filename#, get_endresults_filenames
import os, pickle, pandas as pd
from ..tdms.content import Reader as tdms, read as tdms_content

# def pipeline_end_result(*, session_details, **kwargs):
#     local_log = get_local_logger()
    
#     filenames = get_endresults_filenames(session_details, makedirs = True)
    
#     for item in kwargs.keys() :
#         if not item in filenames.keys():
#             raise NotImplementedError(f"The only possible values saved as end results so far are : {filenames.keys()}")
    
#     kept_keys = set(kwargs.keys()).intersection(set(filenames.keys()))
#     local_log.save_info(f"About to write len(kwargs) pandas table files into {[file for file in kept_keys.values()]}")
    
#     for key in kept_keys.keys():
#         pd.to_pickle(kwargs[key], kept_keys[key])
    
#     local_log.save_info("Writting successfull")

def preprocessed_data(dumped_object, session_details, alf_identifier, extra = () ):

    local_log = get_local_logger()
    filename = get_preprocessed_filename(session_details , alf_identifier, extra, makedirs = True)
    overwriting_info = "(overwriting)" if os.path.isfile(filename) else ""
    local_log.save_info(f"Saving processed {alf_identifier} data at {filename} {overwriting_info}")
    if isinstance(dumped_object, pd.DataFrame):
        dumped_object.to_pickle(filename)
    else :
        with open(filename,"wb") as f :
            pickle.dump(dumped_object, f)
        
def mask(array, session_details, alf_identifier , extra = None, collection = ""):
    """
    Array 
    Session_details is to get access to the session folder to save the mask (by default on the root of the session)
    alf_identifier 

    Parameters
    ----------
    array : TYPE
        This is the nupy array that you want to save as mask..
    session_details : pd.series or AttrDict (contains session  infos)
        This is used to get access to the session folder to save the mask (by default on the root of the session).
    alf_identifier : str
        alf (for alyx filename) identifier is a string that gives info about what is the content of the mask you saved. It will be used in the file name.
        For example, "C1" for a mask with C1. Don't add "mask" in your identifier name, as mask will wanyway be added in the name of the file.
        ( An example finished filename by this function will be as follow : `[session_details.path]/[collection]/mask.[alf_identifier].bmp`).
    extra : str, optional
        If you want specific subcategorical informations to your mask content. 
        For example : 
            Using alf_identifier = "barrel"
            and 
            extra = "C1" or "D1" :
            The resulting filename will be : `.../mask.barrels.C1.bmp` or `.../mask.barrels.D1.bmp` 
        The default is None.
    collection : str, optional
        The subfolder(s) (inside the session_details.path) to save the mask into. The default is "".
        If wou want multiple subfolders, you can specify : collection = "masks/whiskers" for example.

    Returns
    -------
    None.

    """
    from one.alf.spec import to_alf
    import numpy as np, cv2
    local_log = get_local_logger()
    
    filename = to_alf("mask",
                alf_identifier ,
                extension  = "bmp" ,
                namespace = None,
                timescale = None,
                extra = extra)
    
    dirpath = os.path.join(session_details.path,collection)
    if not os.path.isdir(dirpath):
        os.makedirs(dirpath)
    
    filepath = os.path.join(dirpath,filename)
    
    array = np.array(array,dtype = np.uint8)
    array = np.where(array==1, 255, array)
    
    try :
        result = cv2.imwrite(filepath, array)
        if result :
            local_log.save_info(f'{alf_identifier} mask saved')
        else:
            local_log.warning("Error while saving mask at path {filepath}: cv2.imwrite returned False. Check if the resulting file is satisfactory")
    except IOError as e :
        local_log.warning(f'Error while saving mask at path: {filepath}. Original error : {e}')