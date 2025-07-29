# -*- coding: utf-8 -*-
"""
Created on Tue Dec 13 15:05:55 2022

@author: tjostmou

This code defines a class named Reader, which is a subclass of the ScanImageTiffReader class from the ScanImageTiffReader module. The Reader class has several methods for interacting with TIFF (Tagged Image File Format) files, including:

    - delayed_data: This method returns an object that can be used to access the data from the TIFF file on demand. The object is an instance of the DelayedFramesArray class, and is initialized with a _DelayedData object that has information about the channel and plane to access, and the shape of the TIFF file.

    - data: This method returns a subset of the data from the TIFF file. It takes several optional arguments: channel, plane, beg, and end. These arguments can be used to specify which channels and planes of the TIFF file to include in the returned data, and which range of frames to include.

    - structured_data: This method returns the data from the TIFF file, but structured in a dictionary where the keys are the colors of the channels and the values are the data for each channel.

The Reader class also has several class variables and properties, including:

    _data: This variable stores the data from the TIFF file.
    _meta: This variable stores the metadata from the TIFF file.
    _desc: This variable stores the description of a single frame in the TIFF file.
    _step: This property is the number of channels and planes in the TIFF file.
    frame_shape: This property is a tuple containing the width and height of each frame in the TIFF file.
    frame_rate: This property is the frame rate of the TIFF file.
    shape: This property is a tuple containing the number of frames and the width and height of each frame in the TIFF file.

The Reader class also has several methods for accessing information about the channels in the TIFF file, including:

    channels_names: This method returns the names of the channels in the TIFF file.
    channels_colors: This method returns the colors of the channels in the TIFF file.
    channels_indices: This method returns the indices of the channels in the TIFF file.

Finally, the Reader class has several methods for handling warnings and converting metadata strings to dictionaries.

"""

from ScanImageTiffReader import ScanImageTiffReader
from .content import Reader, read, multi_read
from . import content