"""Profile preprocessing."""

import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks
from scipy.stats import linregress

from ..wasserstein import wmean

__all__ = [
    "preprocess",
    "outlier",
    "mean",
]


def preprocess(Y, sigma, std_thres):
    """Preprocess raw profile data.

    Parameters
    ----------
    Y : 1-D array
        1-dimensional profile data.
    sigma : scalar
        Standard deviation of Gaussian filter for smoothing.
    std_thres : scalar
        Standard deviation threshold to detect contact point.

    Returns
    -------
    Y : 1-D array
        Preprocessed profile data.
    L : int
        Length of *Y* until the contact point.

    Notes
    -----
    Profiles undergo the following steps:

    1. Profile direction is set so that the contact point is on the right hand side.
    2. Contact point is detected, and set to have zero height.

    Examples
    --------
    >>> from heavyedge import get_sample_path, RawProfileCsvs
    >>> from heavyedge.api import preprocess
    >>> Y = next(RawProfileCsvs(get_sample_path("Type3")).profiles())
    >>> Y, L = preprocess(Y, 32, 0.01)
    >>> import matplotlib.pyplot as plt  # doctest: +SKIP
    ... plt.plot(Y[:L])
    """
    if Y[0] < Y[-1]:
        # Make plateau is on the left and cp is on the right
        Y = np.flip(Y)

    X = np.arange(len(Y))
    h_xx = gaussian_filter1d(Y, sigma, order=2, mode="nearest")
    if len(h_xx) > 0:
        peaks, _ = find_peaks(h_xx)
    else:
        peaks = np.empty(0, dtype=int)

    candidates = []
    for i, x in enumerate(peaks):
        x = X[x:]
        if not len(x) > 2:
            continue
        y = Y[x]
        reg = linregress(x, y)
        residuals = y - (reg.intercept + reg.slope * x)
        std = np.sqrt(np.sum(residuals**2) / (len(x) - 2))
        if std < std_thres:
            candidates.append(i)

    if candidates:
        cp = peaks[candidates[np.argmax(h_xx[peaks[candidates]])]]
    else:
        cp = len(Y) - 1

    Y = Y - Y[cp]
    return Y, cp + 1


def outlier(profiles, thres=3.5):
    """Detect outlier profiles.

    Parameters
    ----------
    profiles : iterable of array
        Profile data, with last point being the contact point.
    thres : scalar, default=3.5
        Z-score threshold for outlier detection.

    Returns
    -------
    is_outlier : array of bool
        Boolean array where True indicates outlier.

    Notes
    -----
    Outliers are detected by applying modified Z-score method [1]_ on cross-sectional
    areas.

    References
    ----------
    .. [1] Boris Iglewicz and David C Hoaglin.
       Volume 16: how to detect and handle outliers. Quality Press, 1993.

    Examples
    --------
    >>> from heavyedge import get_sample_path, ProfileData
    >>> from heavyedge.api import outlier
    >>> with ProfileData(get_sample_path("Prep-Type3.h5")) as data:
    ...     profiles = list(data.profiles())
    ...     is_outlier = outlier(profiles, 1.5)
    >>> import matplotlib.pyplot as plt  # doctest: +SKIP
    ... for profile, skip in zip(profiles, is_outlier):
    ...     if skip:
    ...         plt.plot(profile, color="red")
    ...     else:
    ...         plt.plot(profile, alpha=0.2, color="gray")
    """
    x = np.array([np.sum(p) for p in profiles])
    med = np.median(x)
    mad = np.median(np.abs(x - med))
    mod_z = 0.6745 * (x - med) / mad
    return np.abs(mod_z) > thres


def mean(x, profiles, grid_num):
    """Fréchet mean of profiles using Wasserstein distance.

    Parameters
    ----------
    x : ndarray
        X coordinates of *profiles*.
    profiles : list of array
        Profile data, with last point being the contact point.
    grid_num : int
        Number of sample points in [0, 1] to construct regression results.

    Returns
    -------
    ndarray
        Averaged *Y*.

    Examples
    --------
    >>> from heavyedge import get_sample_path, ProfileData
    >>> from heavyedge.api import mean
    >>> with ProfileData(get_sample_path("Prep-Type3.h5")) as data:
    ...     x = data.x()
    ...     profiles = list(data.profiles())
    >>> mean = mean(x, profiles, 100)
    >>> import matplotlib.pyplot as plt  # doctest: +SKIP
    ... for profile in profiles:
    ...     plt.plot(profile, alpha=0.2, color="gray")
    ... plt.plot(mean)
    """
    xs, areas, pdfs = [], [], []
    for prof in profiles:
        x_ = x[: len(prof)]
        A = np.trapezoid(prof, x_)
        xs.append(x_)
        areas.append(A)
        pdfs.append(prof / A)
    X, F = wmean(xs, pdfs, grid_num)
    # Fix the last point of X to grid
    last_idx = np.argmin(np.abs(x - X[-1]))
    X[-1] = x[last_idx]

    shape = np.interp(x[: last_idx + 1], X, F)
    shape /= np.trapezoid(shape, x[: len(shape)])
    return shape * np.mean(areas)
