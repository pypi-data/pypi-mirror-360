import numpy as np
from gwpy.timeseries import TimeSeries


class CosineGaussian:
    def __init__(self, parameters):
        """
        Class to generate a cosine Gaussian waveform
        The ``parameters`` dictionary can
        contain the following:

        Parameters
        ----------
        waveform_dict: dict
            Dictionary containing waveform parameters, the parameters
            are:
            - amplitude: Amplitude of the waveform, optional, default is 1.0
            - frequency: Frequency of the waveform, optional, deefault is 100.0
            - duration: Duration of the waveform, required
            - delay: Delay of the waveform, optional, default is 0.0
            - sample_rate: Sample rate of the waveform, optional, default is 16384.0
        Returns
        -------
        timeseries: TimeSeries
            TimeSeries object containing the waveform
        """
        self.params = self._validate_params(parameters)

    @staticmethod
    def _validate_params(parameters):
        default_params = {
            "amplitude": 1.0,
            "frequency": 100.0,
            "duration": None,
            "delay": 0.0,
            "sample_rate": 16384.0,
        }

        waveform_params = parameters.copy()
        for key in default_params:
            if key not in parameters:
                waveform_params[key] = default_params[key]

        if waveform_params["duration"] is None:
            raise ValueError("Duration is not specified")

        return waveform_params

    def __call__(self):
        return self._evaluate_model()

    def _evaluate_model(self):
        sample_rate = self.params["sample_rate"]
        delay = self.params["delay"]
        duration = self.params["duration"]
        frequency = self.params["frequency"]

        m = int(6 * duration * sample_rate)
        if m > int(sample_rate) // 2 - 1:
            m = int(sample_rate) // 2 - 2

        # Normalization computation
        # [Only positive time]
        t_norm = np.arange(0, m, 1) / sample_rate
        g_norm = 2 * np.exp(-t_norm**2 / (2 * duration**2)) * np.cos(2 * np.pi * frequency * t_norm)
        norm_sum = np.sum(g_norm**2)
        amplitude = self.params["amplitude"] * np.sqrt(sample_rate / norm_sum)

        # Compute the signal 
        # [Negative time included] 
        t = np.arange(-m+1, m) / sample_rate
        g = amplitude * np.exp(-t**2 / (2 * duration**2)) * np.cos(2 * np.pi * frequency * t)

        timeseries = TimeSeries(g, t0=t[0], sample_rate=sample_rate, name='cosine_gaussian')
        return timeseries

class CosineGaussianQ(CosineGaussian):
    def __init__(self, parameters):
        """
        Class to generate a cosine Gaussian waveform with Q
        and frequency. This is a subclass of the CosineGaussian
        class.
        The ``parameters`` dictionary can
        contain the following:

        Parameters
        ----------
        waveform_dict: dict
            Dictionary containing waveform parameters, the parameters
            are:
            - amplitude: Amplitude of the waveform, optional, default is 1.0
            - frequency: Frequency of the waveform, required
            - Q: Quality factor of the waveform, required. 
            From it the duration is computed as 
            duration = Q / (2 * pi * frequency)
            - delay: Delay of the waveform, optional, default is 0.0
            - sample_rate: Sample rate of the waveform, optional, default is 16384.0
        Returns
        -------
        timeseries: TimeSeries
            TimeSeries object containing the waveform
        """ 
        parameters = self._validate_params_CGQ(parameters)
        super(CosineGaussianQ, self).__init__(parameters)

    @staticmethod
    def _validate_params_CGQ(parameters):
        default_params = {
            "amplitude": 1.0,
            "frequency": None,
            "Q": None,
        }

        waveform_params = parameters.copy()
        for key in default_params:
            if key not in parameters:
                waveform_params[key] = default_params[key]

        if waveform_params["frequency"] is None:
            raise ValueError("Frequency is not specified")

        if waveform_params["Q"] is None:
            raise ValueError("Q is not specified")

        waveform_params["duration"] = waveform_params["Q"] / (np.pi * 2 * waveform_params["frequency"])

        return waveform_params

    
