import os
import time
from datetime import datetime

import numpy as np
import scipy.io as spio

start_time = time.time()
print(datetime.now())
print()


def get_attributes(fname):
    attr = fname.split('.')[0].split('-')
    dialect = attr[0]
    gender = attr[1][0]
    speaker_id = attr[1]
    sentence_type = attr[2][:2]
    return dialect, gender, speaker_id, sentence_type


INPUT_FOLDER = '../data/preprocessed/train'
TRAIN_FOLDER = '../data/normalized/train'
TEST_FOLDER = '../data/normalized/test'

files = [f for f in os.listdir(INPUT_FOLDER) if os.path.isfile(os.path.join(INPUT_FOLDER, f))]
train = {}
test = {}


def hamming(x, win_size=10, hop_size=3):
    r, c = x.shape
    y = []
    for i in range(0, c, hop_size):
        if i + win_size > c:
            break
        y.append(x[:, i:i + win_size].T.flatten())
    return np.array(y)


# split train test
for file in files:
    input_path = os.path.join(INPUT_FOLDER, file)
    dialect, gender, speaker_id, sentence_type = get_attributes(file)
    if sentence_type == 'SA':
        test.setdefault(speaker_id, []).append(file)
    else:
        train.setdefault(speaker_id, []).append(file)


def smvn(flist):
    data = []
    orig = []
    for fname in flist:
        filedata = spio.loadmat(os.path.join(INPUT_FOLDER, fname))['data']
        orig.append((fname, filedata))
        ft = filedata.T # dim(ft) = (k,39)
        for frame in ft:
            data.append(frame)  # dim(x) => (390,)
    data = np.array(data)

    # zero-mean and unit-variance normalization => (x - mean)/std
    mean = data.mean()
    std = data.std()

    for fname, filedata in orig:
        filedata = hamming((filedata - mean) / std)
        # np.save(os.path.join(TRAIN_FOLDER, fname[:-4]), filedata)
        spio.savemat(os.path.join(TRAIN_FOLDER, fname), dict(data=filedata))
        print('Written', fname)


def mvn(fname):
    filedata = spio.loadmat(os.path.join(INPUT_FOLDER, fname))['data']

    # zero-mean and unit-variance normalization => (x - mean)/std
    mean = filedata.mean()
    std = filedata.std()

    filedata = hamming((filedata - mean) / std)
    # np.save(os.path.join(TEST_FOLDER, fname[:-4]), filedata)
    spio.savemat(os.path.join(TEST_FOLDER, fname), dict(data=filedata))
    print('Written', fname)


# SMVN train
for key, flist in train.items():
    smvn(flist)

# mvn test
for key, flist in test.items():
    for fname in flist:
        mvn(fname)

print('Done')
print(datetime.now())
print("Total time: %s seconds" % (time.time() - start_time))
