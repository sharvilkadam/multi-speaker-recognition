import speech_recognition as sr
from os import path


def speechToText(audioPath):
	AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), audioPath)
	r = sr.Recognizer()
	with sr.AudioFile(AUDIO_FILE) as source:
		audio = r.record(source)  
	try:
		# for testing purposes, we're just using the default API key
		# to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
		# instead of `r.recognize_google(audio)`
		text = r.recognize_google(audio)
		#print("Google Speech Recognition thinks you said " + text)
	except sr.UnknownValueError:
		text = 'Google Speech Recognition could not understand audio'
		#print("Google Speech Recognition could not understand audio")
	except sr.RequestError as e:
		text = 'Could not request results from Google Speech Recognition service'
		#print("Could not request results from Google Speech Recognition service; {0}".format(e))
	return text
