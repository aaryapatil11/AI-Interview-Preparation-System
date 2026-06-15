from ai_helper import model


interview_questions = [
    "Tell me about yourself.",
    "Explain your final year project.",
    "What technologies did you use in your project?",
    "What challenges did you face while building your project?",
    "Why should we hire you?",
    "What are your strengths?",
    "What are your weaknesses?",
    "Where do you see yourself in five years?",
    "Explain one project from your resume.",
    "Do you have any questions for us?"
]


def generate_interview_feedback(question, answer):
    try:
        prompt = f"""
You are an interview evaluator.

Question:
{question}

Candidate Answer:
{answer}

Give feedback in this format:

1. Score out of 10
2. Communication Feedback
3. Content Quality
4. What was good
5. What to improve
6. Better sample answer

Keep it simple for a fresher student.
"""

        response = model.generate_content(prompt)
        return response.text

    except Exception:
        return """
1. Score out of 10
6/10

2. Communication Feedback
Your answer is understandable, but it can be more structured.

3. Content Quality
You answered the question, but add more clear examples.

4. What was good
- You attempted the answer.
- You explained your point simply.

5. What to improve
- Add project details.
- Speak confidently.
- Use examples.
- Avoid very short answers.

6. Better sample answer
Start with a short introduction, explain your skills, mention one project, and end with your career goal.
"""