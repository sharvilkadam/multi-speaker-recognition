import numpy as np
from scipy.signal import spectrogram


def powspec(x, sample_rate, win_time=0.025, step_time=0.010, dither=1):
	win_pts = round(win_time * sample_rate)
	step_pts = round(step_time * sample_rate)

	nfft = 2 ^ (np.ceil(np.log2(win_pts)))
	window = np.hanning(win_pts)
	noverlap = win_pts - step_pts

	f, t, y = spectrogram(x * 32768, fs=sample_rate, window=window, noverlap=noverlap, nfft=nfft)
	y = np.square(np.abs(y))

	if dither:
		y = y + win_pts

	e = np.log(np.sum(y))

	return y, e


def hz2mel(f, htk=False):
	"""
	Converts frequencies f (in Hz) to mel scale
	:param f: the frequencies in Hz
	:param htk: if True uses the mel acis defined in the HTKBook
	:return: z : the frequencies in mel scale
	"""

	if htk is True:
		z = 2595 * np.log10(1 + f / 700)
	else:
		f_0 = 0
		f_sp = 200 / 3
		brkfrq = 1000
		brkpt = (brkfrq - f_0) / f_sp
		logstep = np.exp(np.log(6.4) / 27)
		linpts = (f < brkfrq)

		z = 0 * f

		z[linpts] = (f[linpts] - f_0) / f_sp
		z[~linpts] = brkpt + (np.log(f[~linpts] / brkfrq)) / np.log(logstep)

	return z


def mel2hz(z, htk=False):
	"""
	Convert mel scale frequencies into Hz
	:param z: Frequencies in mel scale
	:param htk: if True uses the HTK formula
	:return: Frequencies in Hz
	"""

	if htk is True:
		f = 700 * (10 ^ (z / 2595) - 1)
	else:
		f_0 = 0
		f_sp = 200 / 3
		brkfrq = 1000
		brkpt = (brkfrq - f_0) / f_sp
		logstep = np.exp(np.log(6.4) / 27)

		linpts = (z < brkpt)

		f = 0 * z

		f[linpts] = f_0 + f_sp * z[linpts]
		f[~linpts] = brkfrq * np.exp(np.log(logstep) * (z[~linpts] - brkpt))

	return f


def fft2melmx(nfft, sr, nfilts=None, width=1, minfreq=0, maxfreq=None, htkmel=False, constamp=0):
	if maxfreq is None:
		maxfreq = sr / 2

	if nfilts is None:
		nfilts = np.ceil(hz2mel(maxfreq, htkmel) / 2)

	wts = np.zeros((nfilts, nfft))

	# Center freq of each FFT bin
	fftfrqs = np.array([i / nfft * sr for i in range(0, nfft / 2)])

	# Center freq of mel bands - uniformly spaced between limits
	minmel = hz2mel(minfreq, htkmel)
	maxmel = hz2mel(maxfreq, htkmel)
	binfreq = mel2hz(minmel + np.array([i / (nfilts + 1) for i in range(0, nfilts + 1)]) * (maxmel - minmel), htkmel)

	binbin = np.round(binfreq / sr * (nfft - 1))

	for i in range(1, nfilts):
		fs = binfreq[i + [0, 1, 2]]
		fs = fs[2] + width * (fs - fs[2])


def audspec(pspectrum, sr, nfilts, fbtype, minfreq, maxfreq, sumpower, bwidth):
	(nfreqs, nframes) = np.shape(pspectrum)
	nfft = (nfreqs - 1) * 2

	wts = np.ndarray([])

	wts = wts[:, 1:nfreqs]
	if sumpower:
		aspectrum = wts * pspectrum
	else:
		aspectrum = np.square(wts * np.sqrt(pspectrum))

	return aspectrum, wts


def melfcc(samples, sr, win_time=0.025, step_time=0.010, numcep=13, lifterexp=0.6, sumpower=True, preemph=0.97,
		   dither=0,
		   minfreq=0, maxfreq=4000, nbands=40, bwidth=1.0, dcttype=2, fbtype='mel', usecmp=0, modelorder=0, broaden=0,
		   useenergy=0):
	pspectrum, logE = powspec(samples, sr, win_time=win_time, step_time=step_time, dither=dither)

	aspectrum = audspec(pspectrum, sr, nbands, fbtype, minfreq, maxfreq, sumpower, bwidth)
