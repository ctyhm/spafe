import pytest
import numpy as np
import scipy.io.wavfile
from spafe.utils import vis
from spafe.features.psrcc import psrcc
from spafe.utils.exceptions import ParameterError
from spafe.utils.cepstral import cms, cmvn, lifter_ceps


@pytest.fixture
def sig():
    __EXAMPLE_FILE = 'test.wav'
    return scipy.io.wavfile.read(__EXAMPLE_FILE)[1]


@pytest.fixture
def fs():
    __EXAMPLE_FILE = 'test.wav'
    return scipy.io.wavfile.read(__EXAMPLE_FILE)[0]


@pytest.mark.test_id(202)
@pytest.mark.parametrize('num_ceps', [13, 26])
@pytest.mark.parametrize('pre_emph', [False, True])
@pytest.mark.parametrize('nfilts', [32, 48])
@pytest.mark.parametrize('nfft', [256, 512, 1024])
@pytest.mark.parametrize('low_freq', [0, 300])
@pytest.mark.parametrize('high_freq', [2000, 4000])
@pytest.mark.parametrize('dct_type', [1, 2, 4])
@pytest.mark.parametrize('use_energy', [False, True])
@pytest.mark.parametrize('lifter', [0, 5])
@pytest.mark.parametrize('normalize', [False, True])
def test_psrcc(sig, fs, num_ceps, pre_emph, nfilts, nfft, low_freq, high_freq, dct_type,
               use_energy, lifter, normalize):
    """
    test PSRCC features module for the following:
        - check if ParameterErrors are raised for:
                - nfilts < num_ceps
                - negative low_freq value
                - high_freq > fs / 2
        - check that the returned number of cepstrums is correct.
        - check the use energy functionality.
        - check normalization.
        - check liftering.
    """

    # check error for number of filters is smaller than number of cepstrums
    with pytest.raises(ParameterError):
        psrccs = psrcc(sig=sig,
                       fs=fs,
                       num_ceps=num_ceps,
                       nfilts=num_ceps - 1,
                       nfft=nfft,
                       low_freq=low_freq,
                       high_freq=high_freq)

    # check lifter Parameter error for low freq
    with pytest.raises(ParameterError):
        psrccs = psrcc(sig=sig,
                       fs=fs,
                       num_ceps=num_ceps,
                       nfilts=nfilts,
                       nfft=nfft,
                       low_freq=-5,
                       high_freq=high_freq)

    # check lifter Parameter error for high freq
    with pytest.raises(ParameterError):
        psrccs = psrcc(sig=sig,
                       fs=fs,
                       num_ceps=num_ceps,
                       nfilts=nfilts,
                       nfft=nfft,
                       low_freq=low_freq,
                       high_freq=16000)

    # compute features
    psrccs = psrcc(sig=sig,
                   fs=fs,
                   num_ceps=num_ceps,
                   pre_emph=pre_emph,
                   nfilts=nfilts,
                   nfft=nfft,
                   low_freq=low_freq,
                   high_freq=high_freq,
                   dct_type=dct_type,
                   use_energy=use_energy,
                   lifter=lifter,
                   normalize=normalize)

    # assert number of returned cepstrum coefficients
    if not psrccs.shape[1] == num_ceps:
        raise AssertionError

    # check use energy
    if use_energy:
        psrccs_energy = psrccs[:, 0]
        xfccs_energy = psrcc(sig=sig,
                             fs=fs,
                             num_ceps=num_ceps,
                             pre_emph=pre_emph,
                             nfilts=nfilts,
                             nfft=nfft,
                             low_freq=low_freq,
                             high_freq=high_freq,
                             dct_type=dct_type,
                             use_energy=use_energy,
                             lifter=lifter,
                             normalize=normalize)[:, 0]

        np.testing.assert_almost_equal(psrccs_energy, xfccs_energy, 3)

    # check normalize
    if normalize:
        np.testing.assert_almost_equal(
            psrccs,
            cmvn(
                cms(
                    psrcc(sig=sig,
                          fs=fs,
                          num_ceps=num_ceps,
                          pre_emph=pre_emph,
                          nfilts=nfilts,
                          nfft=nfft,
                          low_freq=low_freq,
                          high_freq=high_freq,
                          dct_type=dct_type,
                          use_energy=use_energy,
                          lifter=lifter,
                          normalize=False))), 3)
    else:
        # check lifter
        if lifter > 0:
            np.testing.assert_almost_equal(
                psrccs,
                lifter_ceps(
                    psrcc(sig=sig,
                          fs=fs,
                          num_ceps=num_ceps,
                          pre_emph=pre_emph,
                          nfilts=nfilts,
                          nfft=nfft,
                          low_freq=low_freq,
                          high_freq=high_freq,
                          dct_type=dct_type,
                          use_energy=use_energy,
                          lifter=False,
                          normalize=normalize), lifter), 3)
