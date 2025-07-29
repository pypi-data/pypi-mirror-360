import numpy as np
from numpy.random import default_rng
from numpy.fft import fft, ifft
from gwpy.timeseries import TimeSeries


class WhiteNoiseBurst:
    def __init__(self, parameters):
        """
        Initialize class. The ``parameters`` dictionary can
        contain the following:

        Parameters
        ----------
        waveform_dict: dict
            Dictionary containing waveform parameters
        model: str
            Name of waveform model
        """
        self.params = self._validate_params(parameters)

    @staticmethod
    def _validate_params(parameters):
        default_params = {
            "frequency": None,  # start frequency of the white noise burst
            "bandwidth": None,  # bandwidth of the white noise burst
            "duration": None,  # duration of the white noise burst
            "sample_rate": 16384.0,
            "inj_length": 1.,
            "seed": 0,
            "mode": 0
        }

        waveform_params = parameters.copy()
        for key in default_params:
            if key not in parameters:
                waveform_params[key] = default_params[key]

        missing_params = []
        if waveform_params["frequency"] is None:
            missing_params.append("frequency")
        if waveform_params["bandwidth"] is None:
            missing_params.append("bandwidth")
        if waveform_params["duration"] is None:
            missing_params.append("duration")

        if len(missing_params) > 0:
            raise ValueError("The following parameters are missing: {}".format(missing_params))

        return waveform_params

    def __call__(self):
        frequency = self.params["frequency"]
        bandwidth = self.params["bandwidth"]
        duration = self.params["duration"]
        sample_rate = self.params["sample_rate"]
        inj_length = self.params["inj_length"]
        seed = self.params["seed"]
        mode = self.params["mode"]

        return self._evaluate_model(frequency, bandwidth, duration, sample_rate, inj_length, seed, mode)

    def _evaluate_model(self, frequency, bandwidth, duration, sample_rate, inj_length, seed, mode):

        # np.random.seed(seed)
        rng = default_rng(seed)

        # Generate white gaussian noise 1 sec
        x = rng.normal(0, 1, int(inj_length * sample_rate))
        dt = 1.0 / sample_rate
        df = sample_rate / len(x)

        # Apply a band limited cut in frequency
        X = fft(x)
        if mode == 1:
            # set zero bins outside the range [0,bandwidth/2]
            # Heterodyne up by frequency+bandwidth/2 (move zero frequency to center of desidered band)
            bFrequency = int(frequency / df)
            bBandwidth = int((bandwidth / 2.) / df)
            y = np.zeros_like(X)
            bin = (bFrequency + bBandwidth)
            y[bin] = X[0]
            # y[bin + 1] = X[1]
            for i in range(1, bBandwidth):
                y[bin + i] = X[i]
                # y[bin + 2 * i + 1] = X[2 * i + 1]
                y[bin - i] = X[i]
                # y[bin - 2 * i + 1] = -X[2 * i + 1]
            X = y
        else:
            # Asymmetric respect to the central frequency
            bLow = int(frequency / df)
            bHigh = int((frequency + bandwidth) / df)
            X[:bLow] = 0
            X[bHigh:int(len(X))] = 0
        x = ifft(X)

        # Apply a gaussian shape in time
        function_range = inj_length
        t = np.linspace(0, inj_length, len(x))
        gaussian_envelope = np.exp(-((t - function_range / 2) / duration) **2)
        x *= gaussian_envelope

        # Normalization
        hrss = np.sqrt(np.sum(x.real ** 2) * dt)
        x = (1. / np.sqrt(2.)) * x / hrss

        t_start = -t[-1] / 2
        timeseries = TimeSeries(x.real, t0=t_start, sample_rate=sample_rate, name='white_noise_burst')
        return timeseries

# Add ellipticity support
class WhiteNoiseBurstEllipticity(WhiteNoiseBurst):
    def __init__(self, parameters):
        """
        Class for generating a white noise burst with ellipticity.
        This class inherits from the WhiteNoiseBurst class and
        adds ellipticity support.
        The ``parameters`` dictionary can
        contain the following:
        Parameters
        ----------
        waveform_dict: dict
            Dictionary containing waveform parameters
        model: str
            Name of waveform model
        """
        self.params = self._validate_params_ellipticity(parameters)
        super(WhiteNoiseBurstEllipticity, self).__init__(parameters)

    def _validate_params_ellipticity(self, parameters):
        default_params = {
            "frequency": None,  # start frequency of the white noise burst
            "bandwidth": None,  # bandwidth of the white noise burst
            "duration": None,  # duration of the white noise burst
            "sample_rate": 16384.0,
            "inj_length": 1.,
            "pseed": 0,
            "xseed": 0,
            "mode": 0,
            "ellipticity": None,
        }

        waveform_params = parameters.copy()
        for key in default_params:
            if key not in parameters:
                waveform_params[key] = default_params[key]

        missing_params = []
        if waveform_params["frequency"] is None:
            missing_params.append("frequency")
        if waveform_params["bandwidth"] is None:
            missing_params.append("bandwidth")
        if waveform_params["duration"] is None:
            missing_params.append("duration")
        if waveform_params["ellipticity"] is None:
            missing_params.append("ellipticity")

        if len(missing_params) > 0:
            raise ValueError("The following parameters are missing: {}".format(missing_params))

        return waveform_params
    
    def __call__(self):
        return self._evaluate_model_ellipticity()
    
    def _evaluate_model_ellipticity(self):
        frequency = self.params["frequency"]
        bandwidth = self.params["bandwidth"]
        duration = self.params["duration"]
        sample_rate = self.params["sample_rate"]
        inj_length = self.params["inj_length"]
        pseed = self.params["pseed"]
        xseed = self.params["xseed"]
        mode = self.params["mode"]
        ellipticity = self.params["ellipticity"]


        # generating h_plus and h_cross

        white_noise_burst_plus = WhiteNoiseBurst({
            "frequency": frequency,
            "bandwidth": bandwidth,
            "duration": duration,
            "sample_rate": sample_rate,
            "inj_length": inj_length,
            "seed": pseed,
            "mode": mode})()
        
        white_noise_burst_cross = WhiteNoiseBurst({
            "frequency": frequency,
            "bandwidth": bandwidth,
            "duration": duration,
            "sample_rate": sample_rate,
            "inj_length": inj_length,
            "seed": xseed,
            "mode": mode})()
        # ====================================================================
        # Apply ellipticity
        # ====================================================================
        # Subtitute the following lines with the correct expressions
        h_plus_ellipticity = ( 1./np.sqrt(2.) ) * ( (1. + np.cos(ellipticity)**2)/2. )* white_noise_burst_plus.value 
        h_cross_ellipticity = ( 1./np.sqrt(2.) ) * np.cos(ellipticity) * white_noise_burst_cross.value

        # Create TimeSeries objects
        t_start = white_noise_burst_plus.t0.value

        # =====================================================================
        # Create TimeSeries objects
        # =====================================================================

        h_plus_ellipticity_timeseries = TimeSeries(h_plus_ellipticity, t0=t_start, sample_rate=sample_rate, 
                                                   name='h_plus_WhiteNoiseBurst_ellipticity')
        h_cross_ellipticity_timeseries = TimeSeries(h_cross_ellipticity, t0=t_start, sample_rate=sample_rate, 
                                                    name='h_cross_WhiteNoiseBurst_ellipticity')   

        return h_plus_ellipticity_timeseries, h_cross_ellipticity_timeseries  
    