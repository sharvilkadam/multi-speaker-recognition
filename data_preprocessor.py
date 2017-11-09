import os
import time
from datetime import datetime

import matlab.engine
import numpy as np
from preprocess import preprocess

start_time = time.time()
print(datetime.now())
print()

INPUT_FOLDER = '../data/timit_converted/TRAIN'
OUTPUT_FOLDER = '../data/preprocessed/TRAIN'


def hamming(x, win_size=10, hop_size=3):
    r, c = x.shape
    y = []
    for i in range(0, c, hop_size):
        if i + win_size > c:
            break
        y.append(x[:, i:i + win_size].flatten())
    return np.array(y)


files = [f for f in os.listdir(INPUT_FOLDER) if os.path.isfile(os.path.join(INPUT_FOLDER, f))]

print('Loading matlab engine')
eng = matlab.engine.start_matlab()
eng.addpath(r'rastamat', nargout=0)
print('matlab engine loaded')

num_files = len(files)
print('Number of files:', num_files)
print()

for f in range(len(files)):
    file = files[f]
    input_path = os.path.join(INPUT_FOLDER, file)
    output_path = os.path.join(OUTPUT_FOLDER, file.replace('.wav', '.npy'))

    print('Process file {} of {}: {}'.format(f + 1, num_files, input_path))
    x, bit_rate = preprocess(input_path)
    y = []
    for i in range(len(x)):
        y.append(hamming(np.array(eng.test(matlab.double(x[i].tolist()), float(bit_rate)))))
    print('Writing file {} of {}: {}'.format(f + 1, num_files, output_path))
    np.save(output_path, np.array(y))
    print('Written...\n')

print('Done')
print(datetime.now())
print("Total time: %s seconds" % (time.time() - start_time))
