import os
import numpy as np
from sklearn import preprocessing
from sklearn.externals import joblib
from sklearn.neural_network import MLPClassifier
from record import record_to_file
from preprocess import preprocess_file


def get_immediate_subdirectories(a_dir):
    return [name for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]


def get_ids(id_file):
    import json
    with open(id_file, 'r') as f_json:
        ids = json.load(f_json)
    print('ids =', ids)
    return ids


def concat(x, win_size=10, hop_size=3):
    r, c = x.shape
    y = []
    for i in range(0, c, hop_size):
        if i + win_size > c:
            break
        y.append(x[:, i:i + win_size].T.flatten())
    return np.array(y)


def get_data(raw_file_name):
    proc_file_name = 'speakers/eval.npy'
    preprocess_file(raw_file_name, proc_file_name)

    # concat frames
    features = np.load(proc_file_name)
    frames = concat(features)
    print(frames.shape)

    return frames


def load_model():
    normalizer = joblib.load('model/normalizer.pkl')
    model = joblib.load('model/model.pkl')
    return normalizer, model


def predict(id_file, raw_file_name):
    # load enrolled speakers
    ids = get_ids(id_file)
    speakers = list(ids.keys())
    print('Enrolled speakers:', speakers)

    # load model
    normalizer, model = load_model()

    # load data
    X_eval = get_data(raw_file_name)

    # mean var normalize
    X_eval = normalizer.transform(X_eval)

    # predict
    pred = model.predict(X_eval)
    print('pred', pred)

    # find mode
    from scipy import stats
    spid = stats.mode(pred).mode[0]
    print('ID:', spid)

    # print speaker name:
    for key, val in ids.items():
        if spid == val:
            print('Name:', key)
            return key, val



def test(id_file):
    raw_file_name = 'speakers/eval.wav'
    record_to_file(raw_file_name)
    return predict(id_file, raw_file_name)



if __name__ == '__main__':
    test('speakers/enroll.json')

