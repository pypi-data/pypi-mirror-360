# -*- coding: utf-8 -*-
"""
Created on Thu Jan 12 15:55:25 2023

@author: tjostmou
"""

from ScanImageTiffReader import ScanImageTiffReader

import warnings
import numpy as np
import re, json, os
from ctypes import cdll, c_char_p, c_bool

from typing import Any

tiff_C_lib = cdll.LoadLibrary(os.path.join(os.path.dirname(__file__), "tiff_metadata_parse.dll"))

# Define the arguments and return types of the C primitives functions
tiff_C_lib.strarray_mat_to_py.argtypes = [c_char_p]
tiff_C_lib.strarray_mat_to_py.restype = c_char_p

tiff_C_lib.general_json_formatting.argtypes = [c_char_p, c_bool]
tiff_C_lib.general_json_formatting.restype = c_char_p


def multi_read(
    input_path,
    what=[],
    kwargs_list=[
        {},
    ],
):
    tiff_reader = Reader(input_path)
    results = []
    for _what, _kwargs in zip(what, kwargs_list):

        reading_function = getattr(tiff_reader, _what, None)
        if reading_function is None:
            raise ValueError(
                f"Cannot read {_what} from this file. The class tiff.{Reader} doen't implement such method."
            )
        results.append(reading_function(**_kwargs))
    return results


def read(input_path, what="data", *args, **kwargs):
    tiff_reader = Reader(input_path)

    reading_function = getattr(tiff_reader, what, None)
    if reading_function is None:
        raise ValueError(f"Cannot read {what} from this file. The class tiff.{Reader} doen't implement such method.")
    return reading_function(*args, **kwargs)


class Reader(ScanImageTiffReader):

    def __init__(self, filepath, container_mode=False):
        super().__init__(filepath)
        self.filepath = filepath
        self.container_mode = container_mode
        self._data = None

    class _OnDemandGenerator:
        """
        Yields data from suite2p when asked for by iterating over it (list, for loop, etc) instead of all at once.
        This can help manage the amount of ram usage if working over very long tiff files.
        """

        def __init__(self, channel, plane, parent):
            self.channel = channel
            self.plane = plane
            self.parent = parent

        def get_frame(self, index):
            return self.parent.data(channel=self.channel, plane=self.plane, beg=index, end=index + 1)

    def ondemand_data(self, channel, plane=0):
        from pImage.ondemand import OnDemandArray

        return OnDemandArray(shape=self.shape, generator_parent=self._OnDemandGenerator(channel, plane, self))

    # %% Most important methods

    def timelined_data(
        self,
        channel=None,
        plane=None,
        beg=None,
        end=None,
        strictly_positive=True,
        relative_to="start",
        trigger_offset=None,
        trigger_ids=0,
        prefix="auxTrigger",
    ):

        from timelined_array import TimelinedArray

        data = self.data(channel=channel, plane=plane, beg=beg, end=end, strictly_positive=strictly_positive)
        timeline = self.timeline(
            channel=channel,
            plane=plane,
            beg=beg,
            end=end,
            relative_to=relative_to,
            trigger_offset=trigger_offset,
            trigger_ids=trigger_ids,
            prefix=prefix,
        )
        return TimelinedArray(data, timeline=timeline)

    def data(self, channel=None, plane=None, beg=None, end=None, strictly_positive=True):
        """Channel and plane selection are zero based
        channel = 0 : first channel, channel = 1 : second channel, etc...)

        If the data has multiple planes and/or multiple channels,
        this reader class expects the frames to be interleaved, e.g.

        frame0 = time0_plane0_channel1
        frame1 = time0_plane0_channel2
        frame2 = time0_plane1_channel1
        frame3 = time0_plane1_channel2
        frame4 = time1_plane0_channel1
        frame5 = time1_plane0_channel2
        ...
        """

        def _uninterleave_value(value):
            if value is None:
                return None
            if value > self.shape[0] or value < 0:
                raise ValueError("beg or end must be above 0 and below the maximum legth of frames")
            return value * self._step

        beg = _uninterleave_value(beg)
        end = _uninterleave_value(end)
        if beg is not None and beg == end:
            raise ValueError(
                "beg or end must be different. end must at least be 1 above beg otherwise no data will be returned"
            )

        plane_channel_slicer = self._slicer(channel, plane)
        data = self._interleaved_data(beg=beg, end=end)[plane_channel_slicer]
        if strictly_positive:
            data = data - (
                data.min() - 1
            )  # the lowers data point value will be 1. Regardless of if it was positive or negative before.
        return data

    def structured_data(self, beg=None, end=None, strictly_positive=True):
        structured_data = {}
        for channel_id, channel_color in zip(self.channels_indices(), self.channels_colors()):
            structured_data[channel_color] = self.data(
                channel=channel_id, beg=beg, end=end, strictly_positive=strictly_positive
            )
        return structured_data

    def _interleaved_data(self, beg=None, end=None):
        if beg is None and end is None:
            if self._data is not None:
                return self._data

            _data = super().data()

            if self.container_mode:
                self._data = _data

            return _data
        return super().data(beg=beg, end=end)

    def metadata(self, raw=False) -> dict | str:
        """Returns metadata, either after json and matlab string parsing, to python dictionnary,
        or as standard plain string, if raw = True.

        Args:
            raw (bool, optional): _description_. Defaults to False.

        Returns:
            dict | str: _description_
        """
        if raw:  # return original ScanImageTiffReader metadata string ir raw is True
            return super().metadata()  # get metadata from ScanImageTiffReader

        try:
            return self._meta
        except AttributeError:
            pass

        self._meta = self._meta_to_dict(super().metadata())  # get metadata from ScanImageTiffReader
        # _meta_to_dict converts from string to python dictionnary containing python objects,
        # asserting their types with json

        return self._meta

    def description(self, iframe=0, channel=None, plane=None):

        channel_plane_iframe = self._range(channel, plane)[iframe]

        _desc = super().description(channel_plane_iframe)
        _desc = self._desc_to_dict(_desc)
        return _desc

    def timeline(
        self,
        channel=None,
        plane=None,
        beg=None,
        end=None,
        relative_to="start",
        trigger_offset=None,
        max_burst_interval=0.001,
        **kwargs,
    ):

        frames_time = []
        for i in range(0, self.shape[0], 1):  # self._range(channel,plane):
            frames_time.append(self.description(i, channel=channel, plane=plane)["frameTimestamps_sec"])
        frames_time = np.array(frames_time)

        if relative_to == "start" or relative_to == "custom":
            frames_time -= frames_time[0]

        if relative_to == "custom":
            frames_time -= trigger_offset

        if (
            relative_to == "trigger"
        ):  # use the value at nanargmax trigger to set the offset more precisely in the timeline,
            # important as there is 33 msec per frame, we want to keep subframe resolution as much as possible
            try:
                trigger_line = self.trigger_line(channel=channel, plane=plane, **kwargs)
                trigger_times = trigger_line[~np.isnan(trigger_line)]
            except ValueError:  # if this occurs, we may have a multi-trigger per frame, situation. We report it.
                print(
                    f"Warning, the file {self.filepath} has multiple triggers in the same frame (aka, burst). "
                    "Using allow_multi_trigger=True and ingoring out the noise if able to."
                )  # TODO: add logging here instead
                trigger_line = self.trigger_line(channel=channel, plane=plane, **kwargs, allow_multi_trigger=True)

                flattened_times = np.array([item for array_item in trigger_line for item in array_item])
                trigger_times = flattened_times[~np.isnan(flattened_times)]
                # this is True if triggers are a single_burst, and their diff is lower than max_burst_interval.

            if not np.all(np.diff(trigger_times) <= max_burst_interval):
                raise ValueError(
                    "Multiple triggers detected and appearing to far from eachother to not be a single "
                    f"burst, in the file {self.filepath}. Trigger times : {trigger_times}"
                )

            if trigger_times.size == 0:
                # in case there is no trigger, we raise an error if the user asked for trigger centeredtimeline
                raise ValueError(f"No trigger was found in the file {self.filepath}")
            else:
                # in case of trigger, trigger_time becomes the lowest trigger_times value
                # (a single value if so, or the start of the burst if it was a burst)
                trigger_time = np.min(trigger_times)

            # x -= x[np.nanargmax(trigger_line)]
            frames_time -= trigger_time
            # should return None of warn the user if there was no trigger found in the tiff file trigger line metadata

        slicer = slice(beg, end, 1)
        frames_time = frames_time[slicer]

        return frames_time

    def trigger_line(
        self,
        channel=None,
        plane=None,
        trigger_ids="all",
        prefix="auxTrigger",
        beg=None,
        end=None,
        allow_multi_trigger=False,
    ) -> np.ndarray:
        """
        Parameters:
            channel (int, optional): The channel to retrieve the triggers from. If None, all channels are used.
            plane (int, optional): The plane to retrieve the triggers from. If None, all planes are used.
            trigger_ids (str or int or list, optional): The ids of the triggers to retrieve.
                If 'all', all triggers are retrieved.
            prefix (str, optional): The prefix of the triggers to retrieve.
            beg (int, optional): The starting frame for the range of frames to retrieve the triggers from.
            end (int, optional): The ending frame for the range of frames to retrieve the triggers from.

        Returns:
            dict or numpy array:
                A dictionary containing the triggers as keys and their corresponding values as values
                if `return_index` is None.
                Otherwise the values of the specified trigger.
        """

        def _trigger_name_from_id(number):
            return prefix + str(number)

        if trigger_ids == "all":
            return_index = None
            trigger_names = self.available_triggers(prefix=prefix)
        else:
            if isinstance(trigger_ids, (list, tuple)):
                return_index = None
                trigger_names = [_trigger_name_from_id(nb) for nb in trigger_ids]
            else:
                trigger_names = [_trigger_name_from_id(trigger_ids)]
                return_index = trigger_names[0]

        trigger_lines = {}
        for trigger_name in trigger_names:
            trigger_lines[trigger_name] = []

        for index in range(0, self.shape[0], 1):  # self._range(channel = channel, plane = plane)[slicer] :
            frame_desc = self.description(index, channel=channel, plane=plane)
            for trigger_name in trigger_names:
                value = np.array(frame_desc[trigger_name])

                # if value is a np.array with no dimension, with a single item
                if len(value.shape) == 0:
                    value = value.item()

                # if value is a regular np.array
                elif len(value.shape) == 1:
                    # of size 1, containing a single element
                    if value.shape[0] == 1:
                        value = value[0]

                    # of size 0, containing no element
                    if value.shape[0] == 0:
                        value = np.nan

                    # of size greater than 1, containing several elements
                    else:
                        if allow_multi_trigger:
                            pass  # value stays a np array of several elements in 1D
                        else:
                            raise ValueError(
                                "Cannot identify the moment of the trigger, "
                                f"it appears to be a burst : {value} at frame {index}. "
                                "Consider allowing multi trigers with allow_multi_trigger=True"
                            )
                else:
                    # value is multi dimensionnal (more than 1D) Don't know what to do with that,
                    # report error for implementing this cas if it ever happends.
                    raise NotImplementedError(
                        f"Unable to handle array shape {value.shape} "
                        "in the context of a single frame trigger timepoints"
                    )

                if allow_multi_trigger:
                    # by doing this line, we rehape value into a 1D array of arbitrary lenght,
                    # regardless if it was before a single value or an array already.
                    value = np.asarray(value).reshape(-1)

                trigger_lines[trigger_name].append(value)

        dtype = "O" if allow_multi_trigger else float
        for key in trigger_lines.keys():
            trigger_lines[key] = np.array(trigger_lines[key][slice(beg, end)], dtype=dtype)

        return trigger_lines if return_index is None else trigger_lines[return_index]  # type: ignore

    def available_triggers(self, prefix="auxTrigger"):
        triggers_names = []
        i = 0
        description_frame_0 = self.description(0, channel=0, plane=0)
        while True:
            key = prefix + str(i)
            try:
                description_frame_0[key]
            except KeyError:
                return triggers_names
            triggers_names.append(key)
            i += 1

    # %% Frames related metadata

    @property
    def frame_rate(self):
        return self.SI_infos("scanFrameRate", section="hRoiManager")

    @property
    def frame_shape(self):
        return self.SI_infos("pixelsPerLine", section="hRoiManager"), self.SI_infos(
            "linesPerFrame", section="hRoiManager"
        )

    @property
    def pmt_gains(self):
        pmt_colors = [c.lower() for c in self.SI_infos("names", section="hPmts")]
        pmt_gains = self.SI_infos("gains", section="hPmts")
        c_status = self.channels_activation_status()
        return {color: gain for status, color, gain in zip(c_status, pmt_colors, pmt_gains) if status}

    # %% Channels related metadata
    @property
    def zoom_factor(self):
        return self.SI_infos("scanZoomFactor", section="hRoiManager")

    def channels_offsets(self):
        return self.SI_infos("channelOffset", section="hChannels")

    def channels_names(self, available=False):
        if available:
            return self.SI_infos("channelName", section="hChannels")
        try:
            return self._channels_names
        except AttributeError:
            channels_names = self.SI_infos("channelName", section="hChannels")
            c_status = self.channels_activation_status()
            self._channels_names = []
            for status, name in zip(c_status, channels_names):
                if status:
                    self._channels_names.append(name)
            if not isinstance(self._channels_names, list):
                self._channels_names = [self._channels_names]
        return self._channels_names

    def channels_colors(self, available=False) -> list:
        if available:
            return self.SI_infos("channelMergeColor", section="hChannels")
        try:
            return self._channels_colors
        except AttributeError:
            channels_colors = self.SI_infos("channelMergeColor", section="hChannels")
            c_status = self.channels_activation_status()
            self._channels_colors = []
            for status, color in zip(c_status, channels_colors):
                if status:
                    self._channels_colors.append(color)
            if not isinstance(self._channels_colors, list):
                self._channels_colors = [self._channels_colors]
        return self._channels_colors

    def channel_nb(self, available=False) -> int:
        if available:
            return self.channels_available()
        try:
            return self._channel_nb
        except AttributeError:
            channels_save_status = np.array(self.channels_save_status())
            self._channel_nb = len(channels_save_status[channels_save_status == True])
        return self._channel_nb

    def channels_indices(self):
        return range(self.channel_nb())

    def channels_save_status(self):
        try:
            return self._channels_save_status
        except AttributeError:
            self._channels_save_status = self._make_channels_bool_list(
                self.SI_infos("channelSave", section="hChannels")
            )
        return self._channels_save_status

    def channels_activation_status(self):
        # channels can be active (data gets processed) but if they are not saved, we don't
        # care about them for deinterleaving, so this metadata field should not be very usefull
        try:
            return self._channels_activation_status
        except AttributeError:
            self._channels_activation_status = self._make_channels_bool_list(
                self.SI_infos("channelsActive", section="hChannels")
            )
        return self._channels_activation_status

    def channels_available(self) -> int:
        """
        Get the number of channels available for the acquisition setup construction,from the metadata,
        Does not means that they were used for saving data to this tiff file.

        Returns
        -------
        Int
            The amount of the channels available
        """
        # channelsAvailable
        try:
            return self._channels_available
        except AttributeError:
            self._channels_available = self.SI_infos("channelsAvailable", section="hChannels")
        return self._channels_available

    def _make_channels_bool_list(self, channel_list):
        if not isinstance(channel_list, list):
            channel_list = [channel_list]

        new_channel_list = [False] * self.channels_available()
        for value in channel_list:
            new_channel_list[value - 1] = True
        return new_channel_list

    # %% Plane related methods

    def plane_nb(self):
        # TODO will probably have to change this function when we work with several planes for real.
        # I.E. : not tested in real multiplane data from scanimage tiffs
        try:
            return self._plane_nb
        except AttributeError:
            pass
        try:
            self._plane_nb = (
                self.metadata()["RoiGroups"]["imagingRoiGroup"]["rois"]["discretePlaneMode"] + 1  # type: ignore
            )
        except KeyError:
            warnings.warn("Could not figure out planes number")
            self._plane_nb = 1
        return self._plane_nb

    # %% De-interleaving methods

    def _start_stop_step(self, channel=None, plane=None):

        if plane is None:
            if self.plane_nb() > 1:
                raise ValueError(
                    "This tiff file contains more than one plane, please specify the one you want to access"
                )
            else:
                plane = 0

        if channel is None:
            if self.channel_nb() > 1:
                raise ValueError(
                    "This tiff file contains more than one channel, please specify the one you want to access"
                )
            else:
                channel = 0

        if isinstance(channel, str):
            try:
                channel_index = self.channels_colors(available=True).index(channel)
            except Exception:
                raise ValueError(
                    f"The color {channel} doesn't exist in this tiff file metadata (check with channels_colors())"
                )
            if self.channels_save_status()[channel_index] == False:
                raise ValueError(
                    f"The channel color {channel} asked does exist in the setup metadata but such "
                    "channel wasn't saved in this file (check with channels_colors())"
                )

            channel = 0
            for c_index, is_channel_saved in enumerate(self.channels_save_status()):
                if (
                    is_channel_saved == True and channel_index > c_index
                ):  # corrected a channel mistake here !!!! quite important, need to recheck things prior to this day
                    channel += 1

        if channel > self.channel_nb():
            raise ValueError(f"Channel {channel} asked but this file has only {self.channel_nb()} channel(s)")

        if plane > self.plane_nb():
            raise ValueError(f"Plane {plane} asked but this file has only {self.plane_nb()} channel(s)")

        return (self.channel_nb() * plane) + channel, len(self), self._step

    def _range(self, channel=None, plane=None):
        start, stop, step = self._start_stop_step(channel, plane)
        return range(start, stop, step)

    def _slicer(self, channel=None, plane=None):
        start, _, step = self._start_stop_step(channel, plane)
        return slice(start, None, step)

    @property
    def _step(self):
        return self.channel_nb() * self.plane_nb()

    @property
    def shape(self):
        return (int(super().__len__() / (self._step)), *self.frame_shape)

    # %% metadata processing methods

    def SI_infos(self, info, section="hChannels") -> Any:
        try:
            return self.metadata(raw=False)["SI"][section][info]  # type: ignore
        except KeyError:
            warnings.warn(f"Could not figure out scanimage {section} {info}")
            return []

    @staticmethod
    def _meta_to_dict(meta):
        SIs = []
        JSONs = []
        for item in meta.split("\n"):
            if "SI." in item:  # separate matlab like representation of variables by ScanImage
                SIs.append(item[3:])
            else:  # the rest is expected to be json compliant format
                JSONs.append(item)

        # convert JSONs to dict
        json_string = ""
        for item in JSONs:
            json_string += item
        tiff_metadatas = json.loads(json_string)  # TODO : make a recursive converter to ndarray here

        # convert SIs to dict
        tiff_metadatas["SI"] = {}
        for element in SIs:
            keys, val = Reader._keys_value_from_matobj(element)
            if keys is None:
                continue
            Reader._add_nested_keypair(tiff_metadatas["SI"], keys, val)

        return tiff_metadatas  # return full dict

    @staticmethod
    def _desc_to_dict(desc):
        description_dict = {}
        for element in desc.split("\n"):
            keys, val = Reader._keys_value_from_matobj(element)
            if keys is None:
                continue
            Reader._add_nested_keypair(description_dict, keys, val)

        return description_dict

    @staticmethod
    def _keys_value_from_matobj(matobj):
        matobj = matobj.strip()  # removing outside spaces
        try:
            matkey, matvalue = matobj.split(
                "="
            )  # splits a matlab like string representation of an object into the variable name(key) and content(value)
            # separated by = sign
        except (
            ValueError
        ):  # if the string doesn't contain an equal sign it cannot unpack return into two variables : matkey, matvalue.
            # in that case, we return None as we cannot later add key value pair to the dict
            return None, None
        val = Reader._value_from_matvalue(matvalue)  # get value trying to convert as python type
        keys = Reader._keys_from_matkey(matkey)  # get multiple name keys splited by a dot.
        return keys, val

    @staticmethod
    def _value_from_matvalue(matvalue):
        val = matvalue.strip()  # removing outside spaces
        val = Reader._strarray_mat_to_py(
            val
        )  # convert format from matlab string representation of array into python string representation of array.
        # Does nothing and return original if it does not contain such representation.
        val = Reader._cast_as_python_type(
            val
        )  # convert from string to python type if possible. Otherwise keep string repr
        return val

    @staticmethod
    def _keys_from_matkey(matkey):
        matkey = matkey.strip()  # removing outside spaces
        keys = matkey.split(".")
        return keys

    @staticmethod
    def _strarray_mat_to_py(value, use_c=True):

        if use_c:
            return tiff_C_lib.strarray_mat_to_py(value.encode()).decode()

        sub_patterns = _subs_patterns["_strarray_mat_to_py"]
        for index in range(0, 7):
            value = sub_patterns[index][0].sub(sub_patterns[index][1], value)

        # value = re.sub(r"}","]",value)#change matlab 'cells' to array representation
        # value = re.sub(r"{","[",value)
        #     #value = re.sub(r"(?<!;)(?:\b|\B)( +)(?:\b|\B)(?=[^\]\[]*\])(?!;)",",",value)
        # value = re.sub(r"(?<!\[|;|,)(?<=\b|\B)( +)(?=\b|\B)(?=[^\]\[]*\])(?!(?:,|;)|(?:\w+')|\])",",",value)
        # find spaces inside brackets but not when near a ; and replace them with ,
        # value = re.sub(r"(?<=\])( +)(?=\[)",",",value) # also add coma between enclosed brackets
        # with a space in between e.g. ; ] [  Simpler to do it in two re patterns
        # than making a super huge and complex one to do this in one pass
        #     #value = re.sub(r"([a-zA-Z0-9',\.-]+)(?=[^\]\[]*\])","[\g<1>]",value)#find content between brackets and ;
        #  or between two ; and replace them inside brackets

        #     #in two steps :
        # value = re.sub(r"([^\]\[;]+)(?=;[^\]\[]*\])","[\g<1>]",value)# all nested areas except terminal ones before a
        #  ] and separated by ;
        # value = re.sub(r"(?<=;)([^\]\[;]+)(?=[^\]\[]*\])","[\g<1>]",value)#only terminal areas before a ]
        # and behind a ;

        # value = re.sub(r";(?=.*\])",",",value)#find ; before an end bracket and replace them with ,
        #     #for all the above lines, if the string was not a matlab like array, they didn't replaced anything.
        # Then, we try to see if we could make a python like object with it :
        return value

    @staticmethod
    def _cast_as_python_type(value, use_c=True):

        if use_c:
            temp = tiff_C_lib.general_json_formatting(value.encode(), True).decode()

        else:
            sub_patterns = _subs_patterns["_cast_as_python_type"]
            for index in range(0, 3):
                value = sub_patterns[index][0].sub(sub_patterns[index][1], value)

            # val = re.sub(r"(?:\"|\')",'"',val)
            # val = re.sub(r"(?:t|T)rue","true",val)#ensure bools are lowcaps to be json compliant
            # val = re.sub(r"(?:f|F)alse","false",val)

            temp = sub_patterns[3][0].sub(
                sub_patterns[3][1], value
            )  # we remove external string markers if they are present. If not, output = input

        try:
            # val = json.loads('{"_dummy":' + temp + "}")["_dummy"]#just using a fake json representation if it helps.
            # Seems it isn't necessary for scalar objects
            value = json.loads(temp)  # we try to cast it into a python type
        except json.JSONDecodeError:  # we could't make a python object out of it. Try to make apython string out of it
            # (converting single backslash to doulbe ones for json)
            try:
                temp = '"' + temp + '"'
                temp = re.sub(r"\\", r"\\\\", temp)
                # temp = sub_patterns[4][0].sub(sub_patterns[4][1],temp)
                value = json.loads(temp)
            except json.JSONDecodeError:  # something went wrong, just use it as is then.
                warnings.warn(f"metadata line is not json castable : {temp}")
                pass

        if hasattr(
            value, "__len__"
        ):  # if convertible to nd array, do it, and if single dimension array, keep it as native list type
            value = Reader._arrayify_list(value)
        return value

    @staticmethod
    def _arrayify_list(alist):
        with warnings.catch_warnings():  # temporarily prevents creating arrays from ragged sequences.
            # If so, raises VisibleDeprecationWarning
            warnings.filterwarnings("error", category=np.exceptions.VisibleDeprecationWarning)
            try:
                array = np.squeeze(np.array(alist))
                if len(array.shape) == 1:  # if shape is 1 dimensionnal, converts back to list
                    # if array.shape[0] == 1 : #if array contains only one element, converts back to scalar
                    #    return array.item()
                    return array.tolist()
                return array  # if array shape is above one dimension, converts
            except (
                np.exceptions.VisibleDeprecationWarning,
                ValueError,
            ):  # if array from ragged sequences, don't convert
                pass
        return alist

    @staticmethod
    def _add_nested_keypair(original_dict, key_list, value):

        def key_pair_append(dico, depth):
            nonlocal keylist_len
            local_key = key_list[depth]
            if depth == keylist_len:
                dico[local_key] = value
            else:
                if local_key not in dico:
                    dico[local_key] = {}
                key_pair_append(dico[local_key], depth + 1)

        keylist_len = len(key_list) - 1
        key_pair_append(original_dict, 0)


#### Optimisations to compile re patterns only once at import rather than each time text metadatas are processed
def _compile_patterns(pattern_dict):
    for key in pattern_dict.keys():
        for index_key in pattern_dict[key].keys():
            pattern_dict[key][index_key][0] = re.compile(pattern_dict[key][index_key][0])
    return pattern_dict


_subs_patterns = {
    "_strarray_mat_to_py": {
        0: ["}", "]"],
        1: [r"{", "["],
        2: [r"(?<!\[|;|,)(?<=\b|\B)( +)(?=\b|\B)(?=[^\]\[]*\])(?!(?:,|;)|(?:\w+')|\])", ","],
        3: [r"(?<=\])( +)(?=\[)", ","],
        4: [r"([^\]\[;]+)(?=;[^\]\[]*\])", r"[\g<1>]"],
        5: [r"(?<=;)([^\]\[;]+)(?=[^\]\[]*\])", r"[\g<1>]"],
        6: [r";(?=.*\])", ","],
    },
    "_cast_as_python_type": {
        0: [r"(?:\"|\')", '"'],
        1: [r"(?:t|T)rue", "true"],
        2: [r"(?:f|F)alse", "false"],
        3: [r"^(?:\"|\')+|(?:\"|\')+$", ""],
        4: [r"\\", r"\\\\"],
    },
}

_subs_patterns = _compile_patterns(_subs_patterns)
