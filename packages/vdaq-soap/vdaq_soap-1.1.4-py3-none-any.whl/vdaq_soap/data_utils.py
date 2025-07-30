#!/usr/bin/env python3
"""Collection of utilities for data."""

import time
from vdaq_ana import VDaqData, GTimer, ShowProgress
import numpy as np
from lmfit.models import GaussianModel


def fit_gaussian(n, X, center, width=5.0, amplitude=1):
    """Fit a gaussion.

    Args:
    ----
        n: The bins
        X: the bin edges
        center: The center (or mean) of the gaussian.
        width: the sigma estimate of the gaussion. Defaults to 5.0.
        amplitude: the estimae of the amplitude. Defaults to 1.

    Returns
    -------
        the fit result and a legend

    """
    model = GaussianModel()
    params = model.make_params(amplitude=amplitude, center=center, sigma=width)
    result = model.fit(n, params, x=X)
    legend = r'$\mu$=%.3f $\sigma$=%.3f' % (result.best_values['center'], result.best_values['sigma'])
    return result, legend


def draw_best_fit(ax, result, bins, npts=100, legend=None, color="#fa6e1e"):
    """Draw the best fit."""
    X = np.linspace(bins[0], bins[:-1], num=npts)
    Y = result.eval(param=result.params, x=X)
    ax.plot(X, Y, color=color)
    if legend is not None:
        ax.legend([legend], loc=1)


def open_data_file(ifile):
    """Open a data file."""
    ntry = 10
    while True:
        try:
            if ntry <= 0:
                print("### Could not open the data file\n {}".format(ifile))
                vdaq = None
                break

            vdaq = VDaqData(ifile)
            break

        except Exception:
            print("...Problems opening data file. Waiting for a new try.")
            time.sleep(1.0)
            ntry -= 1

    return vdaq
