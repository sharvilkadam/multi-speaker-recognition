import os
import time
from datetime import datetime

import numpy as np
import sklearn

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

INPUT_FOLDER = '../data/preprocessed/TRAIN_TEST_200'
TRAIN_FOLDER = '../data/normalized/train'
TEST_FOLDER = '../data/normalized/test'

files = [f for f in os.listdir(INPUT_FOLDER) if os.path.isfile(os.path.join(INPUT_FOLDER, f))]
train = {}
test = {}

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
        filedata = np.load(os.path.join(INPUT_FOLDER, fname))
        orig.append((fname, filedata))
        for segment in filedata:
            for x in segment:
                data.append(x) # dim(x) => (390,)
    data = np.array(data)

    # zero-mean and unit-variance normalization => (x - mean)/std
    mean = data.mean()
    std = data.std()

    for fname, filedata in orig:
        for i in range(len(filedata)):
            filedata[i] = (filedata[i]-mean)/std
        np.save(os.path.join(TRAIN_FOLDER, fname), filedata)
        print('Written', fname)

def mvn(fname):
    data = []
    filedata = np.load(os.path.join(INPUT_FOLDER, fname))
    for segment in filedata:
        for x in segment:
            data.append(x)  # dim(x) => (390,)
    data = np.array(data)

    # zero-mean and unit-variance normalization => (x - mean)/std
    mean = data.mean()
    std = data.std()

    for i in range(len(filedata)):
        filedata[i] = (filedata[i] - mean) / std
    np.save(os.path.join(TEST_FOLDER, fname), filedata)
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
