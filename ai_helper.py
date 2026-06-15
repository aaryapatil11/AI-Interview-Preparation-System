import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-2.0-flash")


def generate_ai_feedback(resume_text, job_role, ats_score, missing_keywords):
    try:
        prompt = f"""
You are an expert career counselor.

Resume:
{resume_text[:3000]}

Target Job Role:
{job_role}

ATS Score:
{ats_score}/100

Missing Keywords:
{missing_keywords}

Generate:
1. Resume Improvement Tips
2. Skill Gap Analysis
3. 10 Interview Questions
4. Career Roadmap
5. Recommended Courses

Keep answers simple for a final year engineering student.
"""

        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        print("Gemini Error:", e)

        missing = ", ".join(missing_keywords)

        return f"""
AI service is temporarily unavailable. Showing smart local feedback.

1. Resume Improvement Tips
- Add missing keywords: {missing}
- Add project details related to {job_role}.
- Add tools, technologies, GitHub link, and certifications.
- Use ATS-friendly headings like Skills, Projects, Education, Experience.

2. Skill Gap Analysis
- Target Role: {job_role}
- ATS Score: {ats_score}/100
- Missing Skills: {missing}
- Learn these skills and add practical projects.

3. Interview Questions
1. Tell me about yourself.
2. Explain your final year project.
3. Why did you choose {job_role}?
4. What skills are required for {job_role}?
5. Explain one challenge you solved in your project.
6. What is your strongest technical skill?
7. What are your weaknesses?
8. Why should we hire you?
9. What are your career goals?
10. Do you have any questions for us?

4. Career Roadmap
- Learn fundamentals of {job_role}.
- Build 2 strong projects.
- Upload projects on GitHub.
- Improve LinkedIn profile.
- Practice mock interviews daily.

5. Recommended Courses
- Python Basics
- SQL Basics
- Git and GitHub
- Web Development Basics
- Interview Preparation
"""