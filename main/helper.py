import librosa
import numpy as np
import json
import os
from preprocess import preprocess
from enroll_train import enroll_train
from test import predict
from qa import enroll_answer
from main_speech import respond
import soundfile as sf
import time


NUM_SPEAKERS = 200
record_dir = 'speakers/raw/'
preprocess_dir = 'speakers/preprocessed/'
ID_FILE = 'speakers/enroll.json'
raw_file_name = 'speakers/eval.wav'
pcm_file_name = 'speakers/pcm.wav'


def save(data):
    f = open('response.txt', 'w')
    f.write(data)
    f.close()
    return None

def load():
    f = open('response.txt', 'r')
    message = f.read()
    print(message)
    f.close()
    return message


def process(js):
    opt = js['type'].lower()
    print('type', opt)
    if opt == 'query':
        return save(query(js))
    elif opt == 'enroll':
        return save(enroll(js))
    elif opt == 'resp':
        time.sleep(5)
        return load()
    return None


def query(data):
    y = np.array(data['data']['audio']).flatten()
    sr = data['data']['sampleRate']
    librosa.output.write_wav(raw_file_name, y, sr)
    # Write out audio as 24bit PCM WAV
    sf.write(pcm_file_name, y, sr, subtype='PCM_24')
    speaker, spid = predict(ID_FILE, raw_file_name)
    print()
    print('*** Speaker is:', speaker)
    print('*** ID:', spid)
    print()
    q, ans = respond(pcm_file_name, spid)
    print('Answer:', ans)
    return json.dumps({'speaker': speaker, 'query': q, 'response': ans})


def save_audio(data):
    y = np.array(data['data']['audio']).flatten()
    sr = data['data']['sampleRate']
    speaker_name = data['data']['name']
    speaker_dir = record_dir + speaker_name.strip() + '/'
    if os.path.exists(speaker_dir):
        print('Note: Speaker "{}" is already present'.format(speaker_name))
    else:
        os.makedirs(speaker_dir)
    filename = 'SX.wav'
    librosa.output.write_wav(speaker_dir + filename, y, sr)
    return speaker_name, filename


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
    return ids[speaker_name]


def enroll(data):
    speaker_name, filename = save_audio(data)
    preprocess(record_dir, preprocess_dir, speaker_name, filename)
    spid = add_id(speaker_name)
    sch = data['data']['schedule']
    print('Schedule', sch)
    enroll_answer(1, sch, spid, speaker_name)  # schedule
    enroll_answer(2, speaker_name, spid, speaker_name)
    enroll_train(preprocess_dir, ID_FILE, max_iter=25)
    return "true"

