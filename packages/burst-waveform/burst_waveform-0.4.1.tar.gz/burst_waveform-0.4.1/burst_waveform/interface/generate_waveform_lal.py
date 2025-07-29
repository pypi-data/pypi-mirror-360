import numpy as np

try:
    from burst_waveform.models.sine_gaussian import SineGaussian as pySineGaussian
    from burst_waveform.models.sine_gaussian import SineGaussianQ as pySineGaussianQ
except ImportError:
    print("The burst_waveform package has failed to load, you will not be able to employ Burst Waveform approximants.")

from lalsimulation.gwsignal.core.waveform import CompactBinaryCoalescenceGenerator
from lalsimulation.gwsignal.core import gw as gw
from gwpy.timeseries import TimeSeries

class SineGaussian(CompactBinaryCoalescenceGenerator):
    def __init__(self, **kwargs):
        super(SineGaussian, self).__init__()
        self.model = pySineGaussian
        self._domain = "time"
        self._implemented_domain = "time"
        self._generation_domain = None

    @property
    def metadata(self):
        metadata = {
            "type": "sine_gaussian",
            "f_ref_spin": False,
            "modes": False,
            "polarizations": True,
            "implemented_domain": "time",
            "approximant": "SineGaussian",
            "implementation": "",
            "conditioning_routines": "",
        }
        return metadata

    # def _strip_units(self, waveform_dict):
    #     new_dc = {}
    #     for key in waveform_dict.keys():
    #         new_dc[key] = waveform_dict[key].value
    #     return new_dc

    def generate_td_waveform(self, **parameters):

        gen_wf = self.model(**parameters)
        if self.waveform_dict.get("condition"):
            hp, hc = gen_wf()
        else:
            hp, hc = gen_wf()
        return (hp, hc)


class SineGaussianQ(CompactBinaryCoalescenceGenerator):
    def __init__(self, **kwargs):
        super(SineGaussianQ, self).__init__()
        self.model = pySineGaussianQ
        self._domain = "time"
        self._implemented_domain = "time"
        self._generation_domain = None

    @property
    def metadata(self):
        metadata = {
            "type": "sine_gaussian",
            "f_ref_spin": False,
            "modes": False,
            "polarizations": True,
            "implemented_domain": "time",
            "approximant": "SineGaussianQ",
            "implementation" : "Python",
            "conditioning_routines" : 'gwsignal'
        }
        return metadata

    # def _strip_units(self, waveform_dict):
    #     new_dc = {}
    #     for key in waveform_dict.keys():
    #         new_dc[key] = waveform_dict[key].value
    #     return new_dc
    def generate_td_modes(self, **parameters):
        return 0

    def generate_td_waveform(self, **parameters):
        for key in parameters.keys():
            parameters[key] = parameters[key].value if hasattr(parameters[key], 'value') else parameters[key]
        gen_wf = self.model(parameters)

        hp = gen_wf()

        hp = TimeSeries(hp, t0=0, sample_rate=gen_wf.params['sample_rate'], name='hp')
        hc = TimeSeries(np.zeros(len(hp)), t0=0, sample_rate=gen_wf.params['sample_rate'], name='hc')
        return gw.GravitationalWavePolarizations(hp=hp, hc=hc)