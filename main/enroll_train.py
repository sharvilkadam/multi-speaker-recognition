import os
import numpy as np
from sklearn import preprocessing
from sklearn.externals import joblib
from sklearn.neural_network import MLPClassifier


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


def load_data(preprocess_dir, speakers, idx):
    X_train = []
    Y_train = []

    for speaker in speakers:
        speaker_id = idx[speaker]
        flist = [preprocess_dir + speaker + '/' + 'SX.npy']  # TODO: load file list using os
        for fname in flist:
            features = np.load(fname)
            frames = concat(features)
            for frame in frames:
                X_train.append(frame)
                Y_train.append(speaker_id)

    X_train = np.array(X_train)
    Y_train = np.array(Y_train)

    print(X_train.shape, Y_train.shape)

    return X_train, Y_train


def save_model(normalizer, model):
    if os.path.exists('model/'):
        print('Note: model dir is already present: model/ ')
    else:
        os.makedirs('model/')
    joblib.dump(normalizer, 'model/normalizer.pkl')
    joblib.dump(model, 'model/model.pkl')
    print('normalizer and model saved')


def load_model():
    normalizer = joblib.load('model/normalizer.pkl')
    model = joblib.load('model/model.pkl')
    return normalizer, model


def enroll_train(preprocess_dir, id_file, max_iter=25, load_existing = False):

    # load enrolled speakers
    ids = get_ids(id_file)
    speakers = list(ids.keys())
    print('Enrolling following speakers:', speakers)

    # load data
    X_train, Y_train = load_data(preprocess_dir, speakers, ids)

    # load existing model ?
    if load_existing:
        normalizer, model = load_model()
    else:
        normalizer = preprocessing.StandardScaler().fit(X_train)
        model = MLPClassifier(hidden_layer_sizes=(200,), max_iter=max_iter, alpha=0.5,
                              solver='sgd', verbose=10, tol=1e-3, random_state=1,
                              learning_rate_init=.05, learning_rate='adaptive',
                              warm_start=True)

    # mean var normalize
    X_train = normalizer.transform(X_train)

    # train
    model.fit(X_train, Y_train)
    print("Training set score: %f" % model.score(X_train, Y_train))
    print()

    # save
    save_model(normalizer, model)

if __name__ == '__main__':
    enroll_train('speakers/preprocessed/', 'speakers/enroll.json', max_iter=10, load_existing=False)

