import numpy as np
from numpy.fft import fft, ifft
from gwpy.timeseries import TimeSeries


class Ringdown:
    def __init__(self, parameters):
        """
        Initialize class. The ``parameters`` dictionary can
        contain the following:

        Parameters
        ----------
        parameters: dict
            Dictionary containing waveform parameters, including:
            - frequency: float
                Frequency of the ringdown signal
            - tau: float
                Decay time of the ringdown signal
            - iota: float
                Inclination angle of the ringdown signal
            - sample_rate: float
                Sample rate of the ringdown signal
            - duration: float
                Duration of the ringdown signal
        """
        self.params = self._validate_params(parameters)

    @staticmethod
    def _validate_params(parameters):
        default_params = {
            "frequency": None,  # start frequency of the white noise burst
            "tau": None,  # bandwidth of the white noise burst
            "iota": 90,  # inclination angle
            "sample_rate": 16384.0,
            "duration": 1.,
        }

        waveform_params = parameters.copy()
        for key in default_params:
            if key not in parameters:
                waveform_params[key] = default_params[key]

        missing_params = []
        if waveform_params["frequency"] is None:
            missing_params.append("frequency")
        if waveform_params["tau"] is None:
            missing_params.append("tau")
        if waveform_params["duration"] is None:
            missing_params.append("duration")

        if len(missing_params) > 0:
            raise ValueError("The following parameters are missing: {}".format(missing_params))

        return waveform_params

    def __call__(self):
        """
        Generate the ringdown waveform

        Returns
        -------
        hp: TimeSeries
            TimeSeries object containing the plus polarization of the ringdown waveform
        hc: TimeSeries
            TimeSeries object containing the cross polarization of the ringdown waveform
        """
        frequency = self.params["frequency"]
        tau = self.params["tau"]
        iota = self.params["iota"]
        sample_rate = self.params["sample_rate"]
        duration = self.params["duration"]

        return self._evaluate_model(frequency, tau, iota, sample_rate, duration)

    @staticmethod
    def _evaluate_model(frequency, tau, iota, sample_rate, duration):
        iota *= np.pi / 180

        c2 = np.cos(iota)
        c1 = (1 + c2**2) / 2

        if c1 / c2 < 1e-10:
            c1 = 0

        # Define the sample rate and the time offset
        time_offset = 0.05

        # Generate the time values
        t = np.arange(0, duration, 1/sample_rate) + 1/sample_rate - time_offset

        # Generate the waveform
        #define RD_FORMULA "(((x-1./4./[2]+TMath::Abs(x-1./4./[2]))/2./(x-1./4./[2]))*[0]*TMath::Cos(TMath::TwoPi()*[2]*x)+[1]*TMath::Sin(TMath::TwoPi()*[2]*x))*TMath::Exp(-x/[3])" // Heaviside in cos like Andrea Vicere'

        hp_part = ((t - 1 / (4 * frequency) + np.abs(t - 1 / (4 * frequency))) / 2 / (
                t - 1 / (4 * frequency))) * c1 * np.cos(2 * np.pi * frequency * t)
        hc_part = c2 * np.sin(2 * np.pi * frequency * t)
        factor = np.exp(-t / tau)

        hp = hp_part * factor
        hc = hc_part * factor

        # waveform = (((t - 1 / (4 * frequency) + np.abs(t - 1 / (4 * frequency))) / 2 / (
        #             t - 1 / (4 * frequency))) * c1 * np.cos(2 * np.pi * frequency * t)
        #             - 1j * c2 * np.sin(2 * np.pi * frequency * t)) * np.exp(-t / tau)

        # Apply the time offset
        hp[t < 0] = 0
        hc[t < 0] = 0

        # Normalize the waveform
        hrss = np.sqrt(np.sum(hp**2+hc**2) / sample_rate)
        hp /= hrss
        hc /= hrss

        return (TimeSeries(hp, t0=0, sample_rate=sample_rate, name='ringdown_hp'),
                TimeSeries(hc, t0=0, sample_rate=sample_rate, name='ringdown_hc'))
