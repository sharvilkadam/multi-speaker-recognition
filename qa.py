from os import path
import json

def enroll_answer(question_id, answer, speaker_id, speaker_name):
	a[question_id] =  
	fullpath = '/answers/'+speaker_name+'_ans.json'
	if not path.isfile(fullpath):
		a.append(entry)
		with open(fullpath, mode='w') as f:
			f.write(json.dumps(entry, indent=2))
	else:
		with open(fullpath, 'r') as a_json:
		    ids = json.load(a_json)


def add_question(new_question):
	with open('questions.json', mode='r') as q_json:
		questions = json.load(q_json)
	no_of_questions = len(questions)
	questions[int(no_of_questions+1)] = new_question
	with open('questions.json', mode='w') as q_json:
		q_json.write(json.dumps(questions, indent=2))

if __name__ == '__main__':
	#add_question("What is my schedule")
