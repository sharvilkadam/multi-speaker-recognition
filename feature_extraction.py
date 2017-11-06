from preprocess import preprocess
from librosa.feature import mfcc
import numpy as np

import matlab.engine


def extract_feature(x, sr):
    return mfcc(y=x, sr=sr, n_mfcc=39, n_fft=400, hop_length=160, n_mels=40)


if __name__ == '__main__':
    print('Loading matlab engine')
    eng = matlab.engine.start_matlab()
    eng.addpath(r'rastamat', nargout=0)
    print('matlab engine loaded')

    x, bit_rate = preprocess("input.wav")

    print(x[0].tolist())

    y = extract_feature(x[0], bit_rate)
    print(y.shape)
    print(y.tolist())

    print('x', x[0].shape)
    y2 = np.array(eng.test(matlab.double(x[0].tolist()), float(bit_rate)))
    print(y2.shape)
