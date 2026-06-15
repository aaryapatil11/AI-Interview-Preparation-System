def predict_resume_rank(ats_score):

    if ats_score >= 85:
        candidate_level = "Excellent"
        interview_chance = "Very High"
        selection_probability = 90
        suggestion = "Your resume is strong. Apply confidently for internships and jobs."

    elif ats_score >= 70:
        candidate_level = "Strong"
        interview_chance = "High"
        selection_probability = 75
        suggestion = "Your resume is good. Add more projects and certifications."

    elif ats_score >= 50:
        candidate_level = "Average"
        interview_chance = "Medium"
        selection_probability = 55
        suggestion = "Improve skills and add detailed project descriptions."

    elif ats_score >= 35:
        candidate_level = "Weak"
        interview_chance = "Low"
        selection_probability = 35
        suggestion = "Add more technical skills and improve resume format."

    else:
        candidate_level = "Very Weak"
        interview_chance = "Very Low"
        selection_probability = 20
        suggestion = "Build projects, learn skills, and update your resume."

    return (
        candidate_level,
        interview_chance,
        selection_probability,
        suggestion
    )