from burst_waveform.models import SineGaussianQ, WhiteNoiseBurst
import numpy as np


def test_SGQ():
    params = {
        "amplitude": 1.0,
        "frequency": 300.0,
        "Q": 9
    }

    model = SineGaussianQ(params)
    strain = model()

    assert len(strain) != 0
    assert strain.sample_rate.value == model.params["sample_rate"]
    assert model.params["Q"] / (np.pi * 2 * model.params["frequency"]) == model.params["duration"]


def test_WNB():
    params = {
        'frequency': 2000,
        'bandwidth': 500,
        'duration': 0.05,
        'inj_length': 1,
        'mode': 1
    }

    model = WhiteNoiseBurst(params)
    strain = model()

    assert len(strain) == model.params["sample_rate"] * model.params["inj_length"]
    assert strain.sample_rate.value == model.params["sample_rate"]