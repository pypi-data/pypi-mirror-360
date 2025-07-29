"""
This module provides an interface for generating time-domain waveforms
for gravitational wave signals using different approximants. It includes
classes for generating sine-Gaussian and white noise burst waveforms with
ellipticity effects.
""" 
from ..utils.hrss import compute_hrss

def get_td_waveform(**kwargs):
    """
    Generate a time-domain waveform using the specified parameters.

    Parameters
    ----------
    **kwargs : dict
        Keyword arguments containing parameters for the waveform generation.

    Returns
    -------
    tuple
        A tuple containing the plus and cross polarizations of the waveform.
    """
    approximant = kwargs.get("approximant")
    targeted_hrss = kwargs.get("hrss", None)
    
    if approximant == "SGE":
        from burst_waveform.models.sine_gaussian import SineGaussianQEllipticity
        generator = SineGaussianQEllipticity(kwargs)
    elif approximant == "WNB":
        from burst_waveform.models.white_noise_burst import WhiteNoiseBurstEllipticity
        generator = WhiteNoiseBurstEllipticity(kwargs)
    else:
        raise ValueError(f"Unknown approximant: {approximant}")
    
    hp, hc = generator()

    if targeted_hrss is not None:
        source_hrss = compute_hrss(hp, hc)
        # rescale the waveform
        hp *= targeted_hrss / source_hrss
        hc *= targeted_hrss / source_hrss

    return {
        "type": "polarizations",
        "hp": hp,
        "hc": hc,
    }