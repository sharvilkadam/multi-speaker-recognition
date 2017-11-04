import math
import numpy as np

# % function C = SpectralCentroid(signal,windowLength, step, fs)
# %
# % This function computes the spectral centroid feature of an audio signal
# % ARGUMENTS:
# %  - signal: the audio samples
# %  - windowLength: the length of the window analysis (in number of samples)
# %  - step: the step of the window analysis (in number of samples)
# %  - fs: the sampling frequency
# %
# % RETURNS:
# %  - C: the sequence of the spectral centroid feature
# %

def SpectralCentroid(signal, windowLength, step, fs):
    signal = signal / np.max(np.abs(signal))
    curPos = 0
    L = len(signal)
    numOfFrames = math.floor((L - windowLength) / step) + 1
    H = hamming(windowLength)
    m = np.transpose(((fs / (2 * windowLength)) * [i for i in range(1,windowLength+1)]))
    C = np.zeros(numOfFrames, )
    for i in range(0,numOfFrames):
        window = np.multiply(H, (signal[curPos: curPos + windowLength]))
        FFT = np.abs(np.rfft.fft(window, 2 * windowLength))
        FFT = FFT[:windowLength]
        FFT = FFT / np.max(FFT)
        C[i] = np.sum(np.multiply(m, FFT)) / np.sum(FFT)
        if (np.sum(np.array(window) ** 2) < 0.010):
            C[i] = 0.0;
        curPos = curPos + step

    C = C / (fs / 2)

def hamming(x):
    return 0