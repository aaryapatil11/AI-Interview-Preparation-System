import pyttsx3

engine = pyttsx3.init()

questions = [
    "Tell me about yourself",
    "Explain your final year project",
    "What are your strengths",
    "What are your weaknesses",
    "Why should we hire you"
]

def speak_question(question):
    engine.say(question)
    engine.runAndWait()