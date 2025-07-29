import numpy as np
from gwpy.timeseries import TimeSeries
from burst_waveform.models.cosine_gaussian import CosineGaussianQ

class SineGaussian:
    def __init__(self, parameters):
        """
        Class to generate a sine Gaussian waveform
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

        m = int(6*duration*sample_rate)
        if m > int(sample_rate)/2-1:
            m = int(sample_rate)/2-2

        t = np.arange(0, m, 1)/sample_rate
        g = 2*np.exp(-t*t/2/duration/duration)*np.sin(2*np.pi*frequency*t)
        sum = np.sum(g*g)

        amplitude = self.params["amplitude"]*np.sqrt(sample_rate/sum)

        t = np.arange(1, m, 1)/sample_rate
        g = amplitude*np.exp(-t*t/2/duration/duration)*np.sin(2*np.pi*frequency*t)

        waveform = np.concatenate((-g[::-1], np.zeros(1), g))
        # t = np.concatenate((-t[::-1], np.zeros(1), t))

        timeseries = TimeSeries(waveform, t0=-t[-1], sample_rate=sample_rate, name='sine_gaussian')

        return timeseries


class SineGaussianQ(SineGaussian):
    def __init__(self, parameters):
        """
        Class to generate a sine Gaussian waveform with Q
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
        parameters = self._validate_params_SGQ(parameters)
        super(SineGaussianQ, self).__init__(parameters)

    @staticmethod
    def _validate_params_SGQ(parameters):
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


# Add support for ellipticity
class SineGaussianQEllipticity(SineGaussianQ):
    def __init__(self, parameters):
        """
        Class to generate a sine Gaussian waveform with Q
        and frequency. This is a subclass of the CosineGaussianQ
        class. This class also includes ellipticity in the wavefrm 
        generation.
        The ``parameters`` dictionary can
        contain the following:

        Parameters
        ----------
        waveform_dict: dict
            Dictionary containing waveform parameters, the parameters
            are:
            - amplitude: Amplitude of the waveform
            - frequency: Frequency of the waveform
            - Q: Quality factor of the waveform, from it the duration is
                computed as duration = Q / (2 * pi * frequency)
            - ellipticity: Ellipticity of the waveform
            - delay: Delay of the waveform, optional, default is 0.0
            - sample_rate: Sample rate of the waveform, optional, default is 16384.0
        Returns
        -------
        h_plus : TimeSeries
            TimeSeries object containing the h_plus waveform
        h_cross : TimeSeries 
            TimeSeries object containing the h_cross waveform
    
        """
        
        parameters = self._validate_params_CGQE(parameters)
        super(SineGaussianQEllipticity, self).__init__(parameters)

    @staticmethod
    def _validate_params_CGQE(parameters):
        default_params = {
            "amplitude": 1.0,
            "frequency": None,
            "Q": None,
            "ellipticity": None,
            "sample_rate": 16384.0,
        }

        waveform_params = parameters.copy()
        for key in default_params:
            if key not in parameters:
                waveform_params[key] = default_params[key]

        if waveform_params["frequency"] is None:
            raise ValueError("Frequency is not specified")

        if waveform_params["Q"] is None:
            raise ValueError("Q is not specified")

        if waveform_params["ellipticity"] is None:
            raise ValueError("Ellipticity is not specified")
        
        if waveform_params["ellipticity"] < 0 or waveform_params["ellipticity"] > 2*np.pi:
            raise ValueError("Ellipticity must be between 0 and 1")

        waveform_params["duration"] = waveform_params["Q"] / (np.pi * 2 * waveform_params["frequency"])

        return waveform_params
    

    def __call__(self):
        return self._evaluate_model_with_ellipticity()
    
    
    def _evaluate_model_with_ellipticity(self):
        
        ellipticity = self.params["ellipticity"]
        amplitude = self.params["amplitude"]
        frequency = self.params["frequency"]
        Q = self.params["Q"]
        sample_rate = self.params["sample_rate"]
        duration = self.params["duration"]

        params_SG_and_CG = {
            "amplitude": amplitude,
            "frequency": frequency,
            "Q": Q,
            "sample_rate": sample_rate,
            }
        
        # Compute the signal 
        # ====================================================================
        # Subtitute the following lines with the correct expressions
        m = int(6 * duration * sample_rate)
        t = np.arange(-m+1, m) / sample_rate

        cosine_gaussian = CosineGaussianQ(params_SG_and_CG)()
        sine_gaussian = SineGaussianQ(params_SG_and_CG)()

        h_plus = ( 1./np.sqrt(2.) ) * ( (1. + np.cos(ellipticity)**2)/2. ) * cosine_gaussian.value

        h_cross = ( 1./np.sqrt(2.) ) * np.cos(ellipticity) * sine_gaussian.value

        h_plus_timeseries = TimeSeries(h_plus, 
                                       t0=t[0], 
                                       sample_rate=sample_rate, 
                                       name='h_plus_sine_gaussian_with_ellipticity')
        h_cross_timeseries = TimeSeries(h_cross, 
                                        t0=t[0], 
                                        sample_rate=sample_rate, 
                                        name='h_cross_sine_gaussian_with_ellipticity')
        # ====================================================================
        return h_plus_timeseries, h_cross_timeseries