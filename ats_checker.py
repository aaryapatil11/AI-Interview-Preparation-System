def calculate_ats_score(resume_text, job_role):

    score = 0

    resume_text = resume_text.lower()
    job_role = job_role.lower()

    sections = [
        "skills",
        "education",
        "projects",
        "experience",
        "certification"
    ]

    for section in sections:

        if section in resume_text:
            score += 10

    role_keywords = {

        "python developer": [
            "python",
            "flask",
            "django",
            "sql",
            "api"
        ],

        "web developer": [
            "html",
            "css",
            "javascript",
            "react",
            "bootstrap"
        ],

        "data analyst": [
            "python",
            "sql",
            "excel",
            "power bi",
            "pandas"
        ],

        "java developer": [
            "java",
            "oops",
            "spring",
            "mysql",
            "dsa"
        ],

        "cyber security": [
            "network",
            "linux",
            "security",
            "firewall",
            "cyber"
        ]
    }

    keywords = role_keywords.get(job_role, [])

    matched = []

    for keyword in keywords:

        if keyword in resume_text:
            score += 10
            matched.append(keyword)

    missing = [
        keyword
        for keyword in keywords
        if keyword not in matched
    ]

    if score > 100:
        score = 100

    return score, matched, missing