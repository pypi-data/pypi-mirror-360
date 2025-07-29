from scipy.io import savemat, loadmat  # loadmat is deprecated for recent matlab files
from h5py import File as h5pyFile, Reference as h5pyReference
import numpy as np
from pathlib import Path


class MatlabWriter:
    def __init__(self, filename):
        self.filename = Path(filename)

    def save(self, obj):
        savemat(self.filename, obj)


class MatlabLoader:

    def __init__(self, filename):
        self.filename = filename

    def load(self) -> dict:
        file = h5pyFile(self.filename, "r")
        return self.dereference_mapping(file)

    @staticmethod
    def dereference_numpy(numpy_array, file=None) -> np.ndarray:

        numpy_array = np.squeeze(numpy_array)

        for indices in np.ndindex(numpy_array.shape):
            item = numpy_array[indices]

            if not isinstance(item, h5pyReference):
                return numpy_array

            item = file[item][:]

            if not any(indices):
                output_array = np.empty(numpy_array.shape, dtype=type(item))

            output_array[indices] = item

        try:
            return np.stack(output_array)  # type: ignore
        except ValueError:  # ValueError: all input arrays must have the same shape
            # output_array don't have the same shape, we keep an array of differentely shaped arrays
            return output_array

    @staticmethod
    def dereference_mapping(input_mapping, file=None) -> dict:
        if file is None:
            file = input_mapping

        out_dict = {}
        for key, value in input_mapping.items():
            if key == "#refs#":
                continue

            if hasattr(value, "items"):
                out_dict[key] = MatlabLoader.dereference_mapping(value, file)
            else:
                value = value[:]
                if isinstance(value, np.ndarray):
                    out_dict[key] = MatlabLoader.dereference_numpy(value, file)
                else:
                    out_dict[key] = value

        return out_dict
