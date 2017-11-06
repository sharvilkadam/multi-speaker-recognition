from scipy.io import wavfile
import numpy as np
import os
import shutil
from scipy.signal import medfilt


def short_term_energy(signal, window_length: int, step: int):
	num_of_frames = int((signal.size - window_length) / step) + 1
	e = np.zeros(num_of_frames)
	for window_index in range(0, num_of_frames):
		current_index = window_index * step
		window = signal[current_index:current_index + window_length]
		e[window_index] = (1 / window_length) * np.sum(np.square(window))
	return e


def spectral_centroid(signal, window_length: int, step: int, fs: int):
	num_of_frames = int((len(signal) - window_length) / step) + 1
	h = np.hamming(window_length)
	m = np.transpose(((fs / (2 * window_length)) * np.array([i for i in range(1, window_length + 1)])))
	c = np.zeros(num_of_frames)
	for window_index in range(0, num_of_frames):
		current_index = window_index * step
		window = np.multiply(h, (signal[current_index: current_index + window_length]))
		fft = np.abs(np.fft.rfft(window, 2 * window_length))
		fft = fft[:window_length]
		fft = fft / np.max(fft)
		c[window_index] = np.sum(np.multiply(m, fft)) / np.sum(fft)
		if np.sum(np.square(window)) < 0.010:
			c[window_index] = 0.0
	c = c / (fs / 2)
	return c


def find_maxima(f, step):
	count_maxima = 0
	maxima = np.zeros([2, 0])
	for i in range(0, len(f) - step):
		if i > step:
			if (np.mean(f[i - step:i]) < f[i]) and (np.mean(f[i + 1: i + step + 1]) < f[i]):
				maxima = np.hstack((maxima, np.array([[i], [f[i]]])))
				count_maxima = count_maxima + 1
		else:
			if (np.mean(f[0:i + 1]) <= f[i]) and (np.mean(f[i + 1: i + step + 1]) < f[i]):
				maxima = np.hstack((maxima, np.array([[i], [f[i]]])))
				count_maxima = count_maxima + 1

	maxima_new = np.zeros((2, count_maxima))
	count_new_maxima = 0
	i = 0

	while i < count_maxima:
		temp_max = np.array([maxima[0][i]])
		temp_val = np.array([maxima[1][i]])

		while (i < count_maxima - 1) and (maxima[0][i + 1] - temp_max[-1] < step / 2):
			i = i + 1
			np.append(temp_max, maxima[0][i])
			np.append(temp_val, maxima[1][i])

		mi = temp_val.argmax()
		mm = temp_val[mi]

		if mm > 0.02 * f.mean():
			maxima_new[0][count_new_maxima] = temp_max[mi]
			maxima_new[1][count_new_maxima] = f[int(maxima_new[0][count_new_maxima])]
			count_new_maxima = count_new_maxima + 1

		i = i + 1

	maxima = maxima_new
	count_maxima = count_new_maxima

	return maxima, count_maxima


def calc_histogram_boundary_centers(hist_bounds):
	bounds = len(hist_bounds) - 1
	centers = np.zeros(bounds)
	for i in range(0, bounds):
		centers[i] = (hist_bounds[i] + hist_bounds[i + 1]) / 2
	return centers


def preprocess(filename, debug=False):
	# Read the wave file
	bit_rate, raw_wav = wavfile.read(filename)

	# Scale the maximum of absolute amplitude to 1
	# processed_wav = (raw_wav - raw_wav.max()) / -raw_wav.ptp()
	processed_wav = raw_wav / raw_wav.max()

	# 50ms window size
	window_size = 0.050

	# 25ms stride
	step_size = 0.025

	# Compute short-term energy and spectral centroid of the signal
	eor = short_term_energy(processed_wav, int(window_size * bit_rate), int(step_size * bit_rate))
	cor = spectral_centroid(processed_wav, int(window_size * bit_rate), int(step_size * bit_rate), bit_rate)

	# Apply median filtering in the feature sequence twice
	smoothing_step_size = 7
	E = medfilt(medfilt(eor, [smoothing_step_size]), [smoothing_step_size])
	C = medfilt(medfilt(cor, [smoothing_step_size]), [smoothing_step_size])

	# Get the average values of the smoothed feature sequences
	E_mean = E.mean()
	C_mean = C.mean()

	weight = 6

	# Find energy threshold
	hist_e, bounds_e = np.histogram(E, int(np.round(len(E) / 10)))
	x_e = calc_histogram_boundary_centers(bounds_e)
	maxima_e, count_maxima_e = find_maxima(hist_e, 3)
	if np.size(maxima_e, 1) >= 2:
		t_e = (weight * x_e[int(maxima_e[0][0])] + x_e[int(maxima_e[0][1])]) / (weight + 1)
	else:
		t_e = E_mean / 2

	# Find spectral centroid threshold
	hist_c, bounds_c = np.histogram(C, int(np.round(len(C) / 10)))
	x_c = calc_histogram_boundary_centers(bounds_c)
	maxima_c, count_maxima_c = find_maxima(hist_c, 3)
	if np.size(maxima_c, 1) >= 2:
		t_c = (weight * x_c[int(maxima_c[0][0])] + x_c[int(maxima_c[0][1])]) / (weight + 1)
	else:
		t_c = C_mean / 2

	# Thresholding
	flags1 = E >= t_e
	flags2 = C >= t_c
	flags = flags1 & flags2

	# Speech segments detection
	count = 0
	win = 5
	limits = np.zeros((0, 2)).astype(int)
	while count < len(flags):
		countTemp = 1
		limit1 = 0
		limit2 = 0
		while flags[count] == 1 and count < len(flags):
			if countTemp == 1:
				limit1 = np.round((count - win + 1) * step_size * bit_rate) + 1
				if limit1 < 1:
					limit1 = 1
			count = count + 1
			countTemp = countTemp + 1

		if countTemp > 1:
			limit2 = np.round((count + win + 1) * step_size * bit_rate)
			if limit2 > len(processed_wav):
				limit2 = len(processed_wav)
			limits = np.append(limits, np.array([[limit1, limit2]]).astype(int), axis=0)

		count = count + 1

	# post process
	# Merge overlapping segments
	run = 1
	while run == 1:
		run = 0
		for i in range(0, limits.shape[0] - 1):
			if limits[i][1] >= limits[i + 1][0]:
				run = 1
				limits[i][1] = limits[i + 1][1]
				limits = np.delete(limits, (i + 1), axis=0)
				break

	# Get final segments
	segments = []
	for i in range(0, limits.shape[0]):
		segments.append(processed_wav[limits[i][0]:limits[i][1] + 1])

	if debug:
		__debug_directory = "debug"
		if os.path.exists(__debug_directory):
			shutil.rmtree(__debug_directory)

		os.makedirs(__debug_directory)

		for i in range(len(segments)):
			wavfile.write(__debug_directory + os.sep + "file" + str(i) + ".wav", bit_rate, segments[i])
			print(segments[i].shape)

	return segments


if __name__ == '__main__':
	preprocess('input.wav', debug=True)
	# preprocess('example.wav', debug=True)
