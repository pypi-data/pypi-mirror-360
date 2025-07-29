"""
Collection of internal utilities (convenience functions and classes) for data handling.
"""
import glob
import hashlib
import os
import numpy as np
try:
    # Python <= 3.9
    from collections import Iterable
except ImportError:
    # Python > 3.9
    from collections.abc import Iterable


class Quantity:
    """Object containing information about a quantity with the corresponding short_name and unit.

    :ivar short_name: The short short_name representing the quantity.
    :ivar quantity: The name of the quantity.
    :ivar unit: The corresponding unit of the quantity.
    """
    def __init__(self, quantity: str, short_name: str, unit: str):
        self.short_name = short_name
        self.unit = unit
        self.name = quantity

    def __eq__(self, other):
        return self.name == other.name and self.short_name == other.short_name and self.unit == other.unit

    @property
    def quantity(self):
        return self.name

    @property
    def label(self):
        return self.short_name

    def __hash__(self):
        return hash(self.short_name)

    def __repr__(self):
        return f"Quantity('{self.name}')"


class Profile:
    """Class containing profile data.
    """
    def __init__(self, profile_id: str, times: np.ndarray, npoints: np.ndarray, depths: np.ndarray, values: np.ndarray):
        self.id = profile_id
        self.times = times
        self.npoints = npoints
        self.depths = depths
        self.values = values

    def __eq__(self, other):
        return self.id == other.id

    def __repr__(self):
        return f"Profile(id='{self.id}', times={self.times}, depths={self.depths}, values={self.values})"


def create_hash(path: str):
    """Returns the md5 hash as string for the given file.
    """
    return str(hashlib.md5(open(path, 'rb').read()).hexdigest())


def scan_directory_smv(directory: str):
    """Scanning a directory non-recursively for smv-files.

    :param directory: The directory that will be scanned for smv files.
    :returns: A list containing the path to each smv-file found in the directory.
    """
    return glob.glob(directory + "/**/*.smv", recursive=True)


def get_smv_file(path: str):
    """Get the .smv file in a given directory.

    :param path: Either the path to the directory containing the simulation data or direct path
        to the .smv file for the simulation in case that multiple simulation output was written to
        the same directory.
    """
    if os.path.isfile(path):
        return path
    elif os.path.isdir(path):
        files = scan_directory_smv(path)
        if len(files) > 1:
            raise IOError("There are multiple simulations in the directory: " + path)
        elif len(files) == 0:
            raise IOError("No simulations were found in the directory: " + path)
        return files[0]
    elif os.path.isfile(path + ".smv"):
        return path + ".smv"
    else:
        raise IOError("The given path does neither point to a directory nor a file: " + path)


class FDSDataCollection:
    """(Abstract) Base class for any collection of FDS data.
    """

    def __init__(self, *elements: Iterable):
        self._elements = tuple(*elements)

    def __getitem__(self, index):
        return self._elements[index]

    def __iter__(self):
        return self._elements.__iter__()

    def __len__(self):
        return len(self._elements)

    def __contains__(self, value):
        return value in self._elements

    def __repr__(self):
        return "[" + ",\n".join(str(e) for e in self._elements) + "]"

    def clear_cache(self):
        """Remove all data from the internal cache that has been loaded so far to free memory.
        """
        for element in self._elements:
            element.clear_cache()
