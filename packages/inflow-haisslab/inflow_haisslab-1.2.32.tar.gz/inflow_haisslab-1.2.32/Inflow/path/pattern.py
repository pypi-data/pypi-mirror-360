# -*- coding: utf-8 -*-
"""
Created on Mon Dec 12 22:12:09 2022

@author: tjostmou
"""

VGAT_MOUSE_NO = r"Vgat.*?(\d{1,3}).*jRGECO"

TIFF_FRAME_NO = r".*(\d{5})\.tiff?$"

TDMS_TRIALS_TABLE_TIME = r"(\d{4}_\d{2}_\d{2}_\d{2}_\d{2})\.tdms$"

TDMS_VIDEO_TRIAL_NO = r".*?(\d+)\.tdms$"

FOV_NO = r"^.*?(?:FOV)?(\d+).*\.(?:(?:PNG)|(?:png))$"

CONDENSED_DATE = r".*?(20\d{4,6}).*?"

SESSION_NO = r".*?20\d{4,6}_(\d).*?"

ALYX_PATH_EID = r"\w+(?:\\|\/)\d{4}\-\d{2}\-\d{2}(?:\\|\/)\d{3}"

IOI_WHISKER = r"^([a-zA-Z0-9]+)"