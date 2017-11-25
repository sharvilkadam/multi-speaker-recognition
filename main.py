from speechToText import speechToText


def get_ids(id_file):
	import json
	with open(id_file, 'r') as f_json:
		ids = json.load(f_json)
	print('ids =', ids)
	return ids




if __name__ == '__main__':
	audioPath = "schedule.wav"
	#print(speechToText(audioPath))
	ids = get_ids('enroll.json')
	speakers = list(ids.keys())
	print(speakers)