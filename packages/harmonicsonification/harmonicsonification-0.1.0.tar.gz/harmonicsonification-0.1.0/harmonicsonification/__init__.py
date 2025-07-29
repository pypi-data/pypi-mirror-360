#  Copyright (c) 2025 Robert Lieck
import abc
import random
from collections import namedtuple

import numpy as np


sampling_rate = 44000


class Audio:
    def __init__(self, freqs, amps):
        self.freqs = freqs
        self.amps = amps
        self._wave = None
        self._audio = None

    @property
    def wave(self):
        if self._wave is None:
            self._wave = sound(lambda time: (self.freqs, self.amps))
        return self._wave

    @property
    def audio(self):
        if self._audio is None:
            import IPython.display
            wave = render(wave=self.wave, normalise=False, fade=True)
            self._audio = IPython.display.Audio(data=wave, rate=sampling_rate)
        return self._audio

    @property
    def html(self):
        return self.audio._repr_html_()

    def display(self):
        import IPython.display
        IPython.display.display(self.audio)


def seed_everything(seed):
    """Set random seed for reproducibility across multiple libraries."""
    random.seed(seed)  # Python's built-in random module
    np.random.seed(seed)  # NumPy's random module


def normalise_wave(wave, max_amp=0.95):
    wave /= abs(wave).max()
    wave *= max_amp


def fade_wave(wave, time=0.01, start=True, end=True):
    # ramp of correct length
    fade_vals = np.linspace(0, 1, int(np.ceil(time * sampling_rate)))
    if start:
        wave[:len(fade_vals)] *= fade_vals
    if end:
        wave[-len(fade_vals):] *= np.flip(fade_vals)


def render(wave, normalise=True, fade=True):
    wave = wave.copy()
    if normalise is True:
        normalise = dict()
    if normalise is not False:
        normalise_wave(wave, **normalise)
    if fade is True:
        fade = dict()
    if fade is not False:
        fade_wave(wave, **fade)
    return wave


def save(wave, file_name, normalise=True, fade=True):
    from scipy.io.wavfile import write
    wave = render(wave=wave, normalise=normalise, fade=fade)
    # convert to 16bit integer
    wave = np.int16(wave * (np.iinfo(np.int16).max - 1))
    write(file_name, sampling_rate, wave)


def sound(func, phases=0., duration=1.):
    # time vector
    time = np.arange(0, duration, 1 / sampling_rate)
    # array of unit-angle steps (corresponding to frequency of 1Hz)
    angle_steps = np.full_like(time, duration * 2 * np.pi / len(time))

    # get frequencies and amplitudes over time
    if callable(func):
        # freqs and amps are given as a function of time
        freq_amps = func(time)
    else:
        # freqs and amps are numerically given
        freq_amps = func
    # if they are not a tuple, assume only frequencies are given
    if not isinstance(freq_amps, tuple):
        freqs = freq_amps
        amps = 1.
    else:
        freqs, amps = freq_amps
    # if they are not 2D, assume they are constant over time and add dimension for broadcasting
    freqs = np.atleast_2d(freqs)
    amps = np.atleast_2d(amps)

    # compute actual wave form
    # effective change of angle for different frequencies (time-dependent)
    angle_steps = angle_steps[:, None] * freqs
    # actual angle at given time corresponds to the accumulated angle steps
    angles = np.cumsum(angle_steps, axis=0) + phases
    # generate oscillations, multiply by amplitudes and sum up
    return (amps * np.sin(angles)).sum(axis=1)


def n_primes(n):
    """ Returns array of first n primes"""
    # https://stackoverflow.com/questions/4911777/finding-first-n-primes
    # https://stackoverflow.com/questions/2068372/fastest-way-to-list-all-primes-below-n
    # https://stackoverflow.com/questions/2068372/fastest-way-to-list-all-primes-below-n-in-python/3035188#3035188
    max_num = int(max(6, np.ceil(n * np.log(n) + n * np.log(np.log(n)))))
    sieve = np.ones(max_num // 3 + (max_num % 6 == 2), dtype=bool)
    for i in range(1, int(max_num ** 0.5) // 3 + 1):
        if sieve[i]:
            k = 3 * i + 1 | 1
            sieve[k * k // 3::2 * k] = False
            sieve[k * (k - 2 * (i & 1) + 4) // 3::2 * k] = False
    p = np.r_[2, 3, ((3 * np.nonzero(sieve)[0][1:] + 1) | 1)]
    return p[:n]


def harmonics(f0, n, prime=True):
    if prime:
        mul = n_primes(n)
        mul[0] = 1
    else:
        mul = np.arange(n) + 1
    return (f0 * mul).astype(float)


def octaves(f0, freqs):
    """Get the octave above f0 for each frequency"""
    return (freqs / f0) // 2


def freqs_to_octave(freqs, f0=None, octs=None):
    """Maps frequencies to octave above f0"""
    assert (f0 is None) != (octs is None), "Have to provide f0 or octs"
    if octs is None:
        octs = octaves(f0, freqs)
    return freqs / (2 ** octs)


def sonify_am(x, f0=110, add_f0=True, f0_amp=1, prime=False, in_octave=False):
    amplitudes = np.abs(np.asarray(x, dtype=float))
    # get amplitudes from point
    if add_f0:
        amps = [f0_amp] + list(amplitudes)
    else:
        amps = amplitudes
    amps = np.array(amps, dtype=float)
    # harmonic frequencies
    freqs = harmonics(f0=f0, n=len(amps), prime=prime)
    if in_octave:
        freqs = freqs_to_octave(f0=f0, freqs=freqs)
    # return audio object
    return Audio(freqs=freqs, amps=amps)


def sonify_fm(x, f0=110, alpha=0.1, amplitudes='exp', add_f0=True, f0_amp=1, prime=False, in_octave=False, **kwargs):
    frequency_shifts = f0 * alpha * np.asarray(x, dtype=float)
    n = len(frequency_shifts)
    # get amplitudes
    if add_f0:
        n += 1
    if amplitudes == 'const':
        amps = np.ones(n) * kwargs.get('c', 1)
    elif amplitudes == 'exp':
        amps = 10 ** (-np.arange(n) / kwargs.get('d', 10))
    elif amplitudes == 'inv':
        amps = kwargs.get('c', 1) / (np.arange(n) ** kwargs.get('p', 1))
    else:
        try:
            amps = list(amplitudes)
        except:
            raise ValueError("Unknown amplitude type and could not convert to list")
    # add fundamental
    if add_f0:
        amps[0] = f0_amp
    # modulate frequencies
    freqs = harmonics(f0=f0, n=n, prime=prime)
    if in_octave:
        octs = octaves(f0=f0, freqs=freqs)
    if add_f0:
        freqs[1:] += frequency_shifts
    else:
        freqs += frequency_shifts
    if in_octave:
        freqs = freqs_to_octave(freqs, octs=octs)
    # return audio object
    return Audio(freqs=freqs, amps=amps)


def sonify(method, x, **kwargs):
    if method == 'am':
        return sonify_am(x, **kwargs)
    elif method == 'fm':
        return sonify_fm(x, **kwargs)
    else:
        raise ValueError(f"invalid method '{method}'; has to be 'am' or 'fm'")


class Transformation(abc.ABC):

    def __init__(self, data=None):
        """
        Initialise object and fit data if provided

        :param data: data to fit or None
        """
        if data is not None:
            self.fit(data)

    @abc.abstractmethod
    def fit(self, data):
        """
        Fit the transformation for given data

        :param data: data to fit
        :return: self object for chaining
        """
        raise NotImplementedError

    @abc.abstractmethod
    def transform(self, data, norm=None):
        """
        Transform given data; has to be called AFTER :meth:`~fit`

        :param data: data to transform
        :param norm: one of [None, 'i', 'individual', 'g', 'global']. If None (default), no normalisation is
         performed; if 'i' or 'individual', each dimension is normalised individually (e.g. by dividing by the
         respective standard deviation); if 'g' or 'global', all dimensions are normalised globally (e.g. by dividing
         by the maximum standard deviation).
        :return: transformed data
        """
        raise NotImplementedError


class PCA(Transformation):

    def __init__(self, data=None):
        from sklearn.decomposition import PCA as sklearn_PCA
        self.pca = sklearn_PCA()
        self.std = None
        self.eig = None
        self.mean = None
        super().__init__(data=data)

    def fit(self, data):
        self.pca.fit(data)
        self.std = np.sqrt(self.pca.explained_variance_)
        self.eig = self.pca.components_
        self.mean = self.pca.mean_
        return self

    def transform(self, data, norm=None):
        data_trans = self.pca.transform(data)
        if norm is None:
            pass
        elif norm in ['i', 'individual']:
            data_trans /= self.std
        elif norm in ['g', 'global']:
            data_trans /= np.max(self.std)
        else:
            raise ValueError(f"Unknown normalisation method '{norm}'")
        return data_trans
