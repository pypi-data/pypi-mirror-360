# -*- coding: utf-8 -*-
"""
Created on Wed Jan 25 15:36:36 2023

@author: tjostmou
"""

import struct, os, numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from scipy.signal import sawtooth
from typing import Tuple


class Reader:

    def __init__(self, filepath):
        """
        Parameters
        ----------
        filepath : str
            path to the file binfile to read.
        """

        self.path = filepath

    def piezzo_stim_data(self, data_rate=200000, bytes_size=8, format="d", byte_order="@"):
        """Returns data formated as piezzo stimulation bin files, to a numpy array.

        Parameters
        ----------
        data_rate : int, optional
            In hertz. The default is 200000.
        bytes_size : TYPE, optional
            size in bytes of one data point. The default is 8.
        format : TYPE, optional
            format of the bytes. The default is 'd', wich correspond to double precision floating point.
            See https://docs.python.org/3/library/struct.html#format-characters for more info.
        byte_order : TYPE, optional
            The organization of the bytes (little or bid endian) in the file. The default is '@', wich corresponds to
            'native'.
            See https://docs.python.org/3/library/struct.html#byte-order-size-and-alignment for more info.

        Returns a
        -------
        TimelinedArray / np.ndarray
            A numpy ndarray with tilemine attached (in seconds) correspunding to the data in the binfile.
        """

        from timelined_array import TimelinedArray

        # read file content
        with open(os.path.abspath(self.path), "rb") as f:
            content = f.read()

        # format data as defined in parameters (float, int, etc...)
        bytes_data = []
        for index in range(0, len(content), bytes_size):
            byte = content[index : index + bytes_size]
            bytes_data.append(struct.unpack(byte_order + format, byte)[0])

        # compute the timeline in second based on number of items in the file and data_rate.
        timeline = np.linspace(0, len(bytes_data) / data_rate, num=len(bytes_data))

        return TimelinedArray(bytes_data, timeline=timeline)  # return the data as a TimelinedArray


class Writer:

    def __init__(self, path):
        """
        Parameters
        ----------
        filepath : str
            path to the folder of the binfile binfile to write.
        """

        self.path = path

    def write(self, data, filename, bytes_size=8, format="d", byte_order="@"):

        file_path = Path(self.path) / filename

        with open(file_path, "wb") as file:
            for index in range(0, len(data), bytes_size):
                byte = data[index : index + bytes_size].item()
                file.write(struct.pack(byte_order + format, byte))

    def train(self, train_duration=1000, frequence=10, duration=30, peak=10, bytes_size=1, ramp=10, off=0, plot=True):
        single_pulse, _ = self.ramp_stimwrite(duration, peak, ramp, off)

        fs = 200000
        total_time = train_duration / 1000
        nb_of_point_total = int(total_time * fs)

        repetition_time = 1 / frequence
        if repetition_time < duration / 1000:

            raise ValueError(
                f"Frequency {frequence}Hz is too large for a pulse duration of length {duration}ms.\n"
                f"Maximum duration for that repretition would be {repetition_time * 1000}"
            )

        point_offset = int(fs / frequence)

        v_total = np.zeros(nb_of_point_total)
        t_total = np.linspace(0, total_time, nb_of_point_total)
        fname = f"{duration}ms_{ramp}ms_{peak}V_{frequence}_{repetition_time}nr.bin "
        position = 0

        while position < v_total.shape[0]:
            v_total[position : position + single_pulse.shape[0]] = single_pulse
            position += point_offset

        if plot:
            plt.plot(t_total, v_total, label=f"duration = {duration}, peak = {peak}, ramp={ramp} '")
            plt.legend(loc=(0.25, 1.015))
            plt.show()

        return v_total, fname

    def ramp_stimwrite(self, fs=200000, duration=30, peak=10, ramp=10) -> Tuple[np.ndarray, str]:
        """Creates a stimulation pattern as a bin file

        Parameters
        ----------
        duration = 30;   int,
        in ms total duration of our stimulus
        peak = 10;       int,
        in Hz amplitude of our stimulus
        ramp = 10;      int
        in ms duration of ramping acceleration and deceleration of our stimulus
        ramp_down = 10; int
        in ms duration for the ramp down of the stimulus
        fs = 20000;     int, optional
        In Hertz, default sampling frequency of our motor
        in volt defines the amplitude of the stimulation using the peak frequency
        StimNr = 1;    int
        Number of stimulations

        """
        total_time = duration / 1000
        ramp_time = ramp / 1000

        nb_of_point_total = int(total_time * fs)
        nb_of_point_ramp = int(ramp_time * fs)

        t_total = np.linspace(0, total_time, nb_of_point_total)
        t_tramp = np.linspace(0, total_time, nb_of_point_ramp)

        v_total = np.zeros(nb_of_point_total)
        v_ramp = np.linspace(0, 2 * np.pi, nb_of_point_ramp)

        up_ramp = (sawtooth(v_ramp, width=1) + 1) / 2
        up_ramp[-1] = 1
        down_ramp = (sawtooth(v_ramp, width=0) + 1) / 2
        down_ramp[-1] = 0
        fname = f"{duration}ms_{ramp}ms_{peak}V_{1}nr.bin "

        v_total[: up_ramp.shape[0]] = up_ramp
        v_total[up_ramp.shape[0] : -down_ramp.shape[0]] = 1
        v_total[-down_ramp.shape[0] :] = down_ramp
        fname = f"{duration}ms_{ramp}ms_{peak}V_{1}nr.bin "

        return v_total * peak, fname
