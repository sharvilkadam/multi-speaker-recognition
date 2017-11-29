import librosa
import numpy as np
import json
import os

record_dir = 'speakers/raw/'

with open('enroll.json', 'r') as f:
    data = json.load(f)

y = np.array(data['data']['audio']).flatten()
sr = data['data']['sampleRate']
name = data['data']['name']
speaker_dir = record_dir + name.strip() + '/'
if os.path.exists(speaker_dir):
    print('Note: Speaker "{}" is already present'.format(name))
else:
    os.makedirs(speaker_dir)

librosa.output.write_wav(speaker_dir + 'SX.wav', y, sr)