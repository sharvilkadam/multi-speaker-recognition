from vad import vad
import librosa
import numpy as np
import os


def preprocess_file(input_path, output_path):

    y, sr = librosa.load(input_path, sr=None)  # set sr=None for orig file sr otherwise it is converted to ~22K

    # scaling the maximum of absolute amplitude to 1
    processed_wav = y / max(abs(y))

    # calc VAD
    segments, sr = vad(processed_wav, sr)
    print('num segments', len(segments))

    if len(segments) > 0:

        # merge all segments
        processed_data = np.hstack(segments)

        # https://groups.google.com/forum/#!topic/librosa/V4Z1HpTKn8Q
        mfcc = librosa.feature.mfcc(y=processed_data, sr=sr, n_mfcc=13, n_fft=(25 * sr) // 1000,
                                    hop_length=(10 * sr) // 1000)
        mfcc[0] = librosa.feature.rmse(processed_data, hop_length=int(0.010 * sr), n_fft=int(0.025 * sr))
        mfcc_delta = librosa.feature.delta(mfcc)
        mfcc_delta2 = librosa.feature.delta(mfcc, order=2)
        features = np.vstack([mfcc, mfcc_delta, mfcc_delta2])

        # save features
        np.save(output_path, features)
        print('Features saved in file:', output_path)

        return output_path

    else:
        print('Error: no voice segments detected in file:', input_path)

    return None



def preprocess(in_dir, out_dir, speaker_name, file_name):
    speaker_dir = out_dir + speaker_name + '/'
    input_path = in_dir + speaker_name + '/' + file_name
    output_path = speaker_dir + file_name[:-4] + '.npy'
    if not os.path.exists(speaker_dir):
        os.makedirs(speaker_dir)
    return preprocess_file(input_path, output_path)


if __name__ == '__main__':
    preprocess('speakers/raw/', 'speakers/preprocessed/', 'Sushant', 'SX.wav')