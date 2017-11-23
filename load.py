# Import required libraries
# Add whatever you want
import numpy as np
import os
import scipy.io as spio

# load data
TRAIN_FOLDER = '../data/normalized/train'
TEST_FOLDER = '../data/normalized/test'
ID_FILE = '../data/normalized/id.json'
NUM_SPEAKERS = 200


def get_attributes(fname):
    attr = fname.split('.')[0].split('-')
    dialect = attr[0]
    gender = attr[1][0]
    speaker_id = attr[1]
    sentence_type = attr[2][:2]
    return dialect, gender, speaker_id, sentence_type


def load_files(train):
    X = []
    Y = []
    for speaker_id, flist in train.items():
        for fname in flist:
            filedata = spio.loadmat(fname)['data']
            for frame in filedata:
                X.append(frame)  # dim(x) => (390,)
                Y.append(speaker_id)
    return X, Y


def load_train_data():
    import json
    with open(ID_FILE, 'r') as f_json:
        ids = json.load(f_json)
    print('ids', ids)

    # train data
    train = {}
    files = [f for f in os.listdir(TRAIN_FOLDER) if os.path.isfile(os.path.join(TRAIN_FOLDER, f))]
    for file in files:
        dialect, gender, speaker_id, sentence_type = get_attributes(file)
        file_path = os.path.join(TRAIN_FOLDER, file)
        if speaker_id not in ids:
            print('ERROR:', speaker_id, 'not found in ids')
        speaker_id = ids[speaker_id]
        train.setdefault(speaker_id, []).append(file_path)

    # test data
    test = {}
    files = [f for f in os.listdir(TEST_FOLDER) if os.path.isfile(os.path.join(TEST_FOLDER, f))]
    for file in files:
        dialect, gender, speaker_id, sentence_type = get_attributes(file)
        file_path = os.path.join(TEST_FOLDER, file)
        if speaker_id not in ids:
            print('ERROR:', speaker_id, 'not found in ids')
        speaker_id = ids[speaker_id]
        test.setdefault(speaker_id, []).append(file_path)

    # load data
    # input_path = os.path.join(TRAIN_FOLDER, file)
    X_train, Y_train = load_files(train)
    X_test, Y_test = load_files(test)
    return np.array(X_train), np.array(Y_train), np.array(X_test), np.array(Y_test)


print('Loading data...')
X_train, Y_train, X_test, Y_test = load_train_data()
from sklearn.utils import shuffle
X_train, Y_train = shuffle(X_train, Y_train)

spio.savemat('dataset.mat', dict(X=X_train, y=Y_train, X_test=X_test, Y_test=Y_test))

print()
print('# Train :', len(Y_train))
print('# Test  :', len(Y_test))
print()