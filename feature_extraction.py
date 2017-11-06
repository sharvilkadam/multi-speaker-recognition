from preprocess import preprocess
from librosa.feature import mfcc


def extract_feature(x, sr):
	return mfcc(y=x, sr=sr, n_mfcc=39, n_fft=25, hop_length=10)


if __name__ == '__main__':
	x, bit_rate = preprocess("input.wav")

	y = extract_feature(x[0], bit_rate)
	print(y.shape)
