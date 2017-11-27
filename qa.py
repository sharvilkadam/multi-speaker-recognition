from os import path
import os
import json

def enroll_answer(question_id, answer, speaker_id, speaker_name):
	apath = '/home/sharvil/deepLearning/projec/python/answers/'
	filename = speaker_name+'_ans.json'
	fullpath = apath + filename
	a = {}
	if not path.exists(apath):
		os.makedirs(apath)
	if not path.isfile(fullpath):
		with open(fullpath, mode='w') as a_json:
			a[question_id] = answer
			a_json.write(json.dumps(a, indent=2))
	else:
		with open(fullpath, mode='r') as a_json:
			answers = json.load(a_json)
		answers[question_id] = answer
		with open(fullpath, mode='w') as a_json:
			a_json.write(json.dumps(answers, indent=2))


def add_question(new_question):
	with open('questions.json', mode='r') as q_json:
		questions = json.load(q_json)
	no_of_questions = len(questions)
	questions[no_of_questions+1] = new_question
	with open('questions.json', mode='w') as q_json:
		q_json.write(json.dumps(questions, indent=2))

def get_answer(question_id, speaker_name):
	apath = '/home/sharvil/deepLearning/projec/python/answers/'
	filename = speaker_name+'_ans.json'
	fullpath = apath + filename
	if path.isfile(fullpath):
		with open(fullpath, mode='r') as a_json:
			answers = json.load(a_json)
		if question_id in answers.keys():
		    return answers[question_id]
		else:
			return answers["0"]
	else:
		return "No answers for "+speaker_name


if __name__ == '__main__':
	#add_question("What is my schedule")
	enroll_answer(3,"Watch the movie U.N.C.L.E.",1,'Vritvij')
	#print(get_answer("1","Vritvij"))
