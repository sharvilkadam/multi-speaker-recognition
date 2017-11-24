import os
from record import record_audio
from preprocess import preprocess
from enroll_train import enroll_train
from test import test


NUM_SPEAKERS = 200
record_dir = 'speakers/raw/'
preprocess_dir = 'speakers/preprocessed/'
ID_FILE = 'speakers/enroll.json'

def option():
    print('1. Record: To record audio for enrolling a new speaker')
    print('2. Enroll: To enroll newly added speakers and fine tune model')
    print('3. Eval: To test enrolled speakers')
    print('4. Exit')
    print()

    while 1:
        opt = input('Enter your choice: ')
        if opt in ['1', '2', '3', '4']:
            return int(opt)
        print('Invalid option:', opt)


def add_id(speaker_name):
    import json

    if os.path.exists(ID_FILE):
        with open(ID_FILE, 'r') as f_json:
            ids = json.load(f_json)
    else:
        ids = {}

    print('ids =', ids)
    if speaker_name in ids:
        print(speaker_name, 'is already present in ids:', ids[speaker_name])
    else:
        val = len(ids.keys())
        ids[speaker_name] = val
        with open(ID_FILE, 'w') as f_json:
            json.dump(ids, f_json)
        print('Speaker', speaker_name, 'is added in ids:', val)
        print('ids =', ids)


def record():
    speaker_name, filename = record_audio(record_dir)
    preprocess(record_dir, preprocess_dir, speaker_name, filename)
    add_id(speaker_name)


def enroll():
    enroll_train(preprocess_dir, ID_FILE)


if __name__ == '__main__':
    while 1:
        print()
        opt = option()
        print()

        if opt == 1:  # Record
            record()
        elif opt == 2:  # Enroll / Train
            enroll()
        elif opt == 3:  # Eval
            test(ID_FILE)
        elif opt == 4:  # Exit
            break

