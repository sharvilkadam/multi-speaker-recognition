from speechToText import speechToText
from qa import *


def get_ids(id_file):
	import json
	with open(id_file, 'r') as f_json:
		ids = json.load(f_json)
	print('ids =', ids)
	return ids


def respond(audioPath, speaker_id):
	audioText = speechToText(audioPath)
	ids = get_ids('enroll.json')
	speakers = list(ids.keys())
	for speaker in speakers:
		if speaker_id == ids[speaker]:
			speaker_name = speaker
			break

	#check if the text is a question or not.

	
	question_id = get_question_id(audioText)
	answer = get_answer(question_id,speaker_name)
	return answer


if __name__ == '__main__':
	#audioPath = "schedule.wav"
	#audioText = speechToText(audioPath)
	#print(audioText)
	#ids = get_ids('enroll.json')
	#speakers = list(ids.keys())
	#print(speakers)
	#print(get_question_id(audioText))
	print(respond("schedule.wav",1))
