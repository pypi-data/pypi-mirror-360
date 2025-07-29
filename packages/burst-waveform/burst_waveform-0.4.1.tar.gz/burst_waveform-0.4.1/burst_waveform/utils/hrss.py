import numpy as np


def compute_hrss(hp, hc):
    """
    Compute the root-sum-square of the strain waveform.

    hrss = sqrt(int dt (hp^2 + hc^2))
    """
    dt = hp.times.value[1] - hp.times.value[0]  # assuming uniform sampling
    integral = np.sum(hp.value**2 * dt + hc.value**2 * dt)
    hrss = np.sqrt(integral)
    return hrss
