"""Processed profile data files."""

import numbers
from collections.abc import Sequence
from pathlib import Path

import h5py
import numpy as np

__all__ = [
    "ProfileData",
]


class ProfileData:
    """Preprocessed 1-dimensional profile data as hdf5 file.

    Parameters
    ----------
    path : pathlike
        Path to the hdf5 file.
    mode : {'r', 'w', 'r+', 'a', 'w-'}
        Mode to open the file.
    kwargs : dict
        Optional arguments passed to :class:`h5py.File`.

    Notes
    -----
    ``self[key]`` returns a tuple of full profile data, profile length(s) and
    profile name(s).
    """

    def __init__(self, path, mode="r", **kwargs):
        self.path = Path(path).expanduser()
        self._file = h5py.File(path, mode, **kwargs)

    def __enter__(self):
        return self

    def __exit__(self, type, value, trace_back):
        self._file.close()

    def __len__(self):
        return self.shape()[0]

    def __getitem__(self, key):
        if isinstance(key, numbers.Integral):
            profile = self._file["profiles"][key]
            length = self._file["len"][key]
            name = str(self._file["names"][key], encoding="utf-8")
            return (profile, length, name)
        elif isinstance(key, (slice, Sequence, np.ndarray)):
            profiles = self._file["profiles"][key]
            lengths = self._file["len"][key]
            names = np.char.decode(
                self._file["names"][key].astype("S"), encoding="utf-8"
            )
            return (profiles, lengths, names)
        else:
            raise TypeError(f"Invalid index type: {type(key)}")

    def close(self):
        self._file.close()

    def create(self, M, resolution, name=None):
        """Create datasets and write metadata.

        Parameters
        ----------
        M : int
            Maximum length of profile data.
        resolution : float
            Spatial resolution of the profile data.
        name : str, optional
            Unique name to identify the dataset.

        Returns
        -------
        obj
            Returns the object itself.
        """
        if name is None:
            name = str(self.path.with_suffix(""))
        self._file.attrs["name"] = name
        self._file.attrs["res"] = resolution

        self._file.create_dataset(
            "profiles",
            (0, M),
            maxshape=(None, M),
            dtype=float,
        )
        self._file.create_dataset(
            "len",
            (0,),
            maxshape=(None,),
            dtype=int,
        )
        self._file.create_dataset(
            "names",
            (0,),
            maxshape=(None,),
            dtype=h5py.string_dtype(),
        )
        return self

    def name(self):
        """Unique name of the dataset.

        Returns
        -------
        str
        """
        return self._file.attrs["name"]

    def resolution(self):
        """Spatial resolution of the profile data.

        Returns
        -------
        float
        """
        return self._file.attrs["res"]

    def shape(self):
        """Shape of profile dataset.

        Returns
        -------
        (N, M)
        """
        return self._file["profiles"].shape

    def x(self):
        """Spatial coordinates.

        Returns
        -------
        (M,) ndarray
        """
        return np.arange(self.shape()[1]) / self.resolution()

    def write_profiles(self, profiles, lengths, names):
        """Append profiles data to file.

        Parameters
        ----------
        profiles : (N, M) ndarray of float
            1-dimensional profile.
        lengths : (N,) array of int
            Number of data in *profiles* from reference point to contact point.
        names : list of str
            Profile names.
        """
        N = len(profiles)

        dset = self._file["profiles"]
        dset.resize(dset.shape[0] + N, axis=0)
        dset[-N:] = profiles

        dset = self._file["len"]
        dset.resize(dset.shape[0] + N, axis=0)
        dset[-N:] = lengths

        dset = self._file["names"]
        dset.resize(dset.shape[0] + N, axis=0)
        dset[-N:] = names

    def profiles(self):
        """Yield profiles.

        Profiles are cropped by the contact point.

        Yields
        ------
        1-D ndarray
        """
        for profile, length in zip(self._file["profiles"], self._file["len"]):
            yield profile[:length]

    def profile_names(self):
        """Yield profile names.

        Yields
        ------
        str
        """
        for name in self._file["names"]:
            yield str(name, encoding="utf-8")

    def all_profiles(self):
        """Return all profiles.

        Returns
        -------
        (N, M) ndarray
            All N profiles data.
        """
        return self._file["profiles"][:]
