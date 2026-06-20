import sqlite3
from io import BytesIO

from flask import Flask, render_template, request, redirect, url_for, session, make_response
from werkzeug.security import generate_password_hash, check_password_hash

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from resume_parser import extract_text_from_pdf
from ats_checker import calculate_ats_score
from ai_helper import generate_ai_feedback
from database import init_db
from interview_helper import interview_questions, generate_interview_feedback
from rank_predictor import predict_resume_rank


app = Flask(__name__)
app.secret_key = "aarya_secret_key"

init_db()


@app.route("/")
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template("index.html", user_name=session["user_name"])


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        try:
            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                (name, email, hashed_password)
            )

            conn.commit()
            conn.close()

            return redirect(url_for("login"))

        except sqlite3.IntegrityError:
            return "Email already registered. Please login."

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()

        conn.close()

        if user and check_password_hash(user[3], password):
            session["user_id"] = user[0]
            session["user_name"] = user[1]
            session["role"] = user[4]

            return redirect(url_for("home"))

        return "Invalid email or password."

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/analyze", methods=["POST"])
def analyze():
    if "user_id" not in session:
        return redirect(url_for("login"))

    resume = request.files["resume"]
    job_role = request.form["job_role"]

    resume_text = extract_text_from_pdf(resume)

    ats_score, matched_keywords, missing_keywords = calculate_ats_score(
        resume_text,
        job_role
    )

    ai_feedback = generate_ai_feedback(
        resume_text,
        job_role,
        ats_score,
        missing_keywords
    )

    candidate_level, interview_chance, selection_probability, rank_suggestion = predict_resume_rank(
        ats_score
    )

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO results (
            user_id,
            filename,
            job_role,
            ats_score,
            matched_keywords,
            missing_keywords,
            ai_feedback
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        session["user_id"],
        resume.filename,
        job_role,
        ats_score,
        ", ".join(matched_keywords),
        ", ".join(missing_keywords),
        ai_feedback
    ))

    conn.commit()
    conn.close()

    return render_template(
        "result.html",
        filename=resume.filename,
        job_role=job_role,
        ats_score=ats_score,
        matched_keywords=matched_keywords,
        missing_keywords=missing_keywords,
        ai_feedback=ai_feedback,
        candidate_level=candidate_level,
        interview_chance=interview_chance,
        selection_probability=selection_probability,
        rank_suggestion=rank_suggestion
    )


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT filename, job_role, ats_score, created_at
        FROM results
        WHERE user_id = ?
        ORDER BY created_at DESC
    """, (session["user_id"],))

    results = cursor.fetchall()

    cursor.execute("""
        SELECT question, answer, feedback, created_at
        FROM interviews
        WHERE user_id = ?
        ORDER BY created_at DESC
    """, (session["user_id"],))

    interviews = cursor.fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        results=results,
        interviews=interviews
    )


@app.route("/download_report")
def download_report():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT filename, job_role, ats_score, matched_keywords,
               missing_keywords, ai_feedback, created_at
        FROM results
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT 1
    """, (session["user_id"],))

    result = cursor.fetchone()
    conn.close()

    if not result:
        return "No report found. Please analyze a resume first."

    filename = result[0]
    job_role = result[1]
    ats_score = result[2]
    matched_keywords = result[3]
    missing_keywords = result[4]
    ai_feedback = result[5]
    created_at = result[6]

    candidate_level, interview_chance, selection_probability, rank_suggestion = predict_resume_rank(
        ats_score
    )

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setTitle("AI Resume Analysis Report")

    width, height = letter
    y = height - 50

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(50, y, "AI Resume Analysis Report")
    y -= 40

    pdf.setFont("Helvetica", 12)

    details = [
        f"File Name: {filename}",
        f"Selected Role: {job_role}",
        f"ATS Score: {ats_score}/100",
        f"Candidate Level: {candidate_level}",
        f"Interview Chance: {interview_chance}",
        f"Selection Probability: {selection_probability}%",
        f"Rank Suggestion: {rank_suggestion}",
        f"Matched Keywords: {matched_keywords}",
        f"Missing Keywords: {missing_keywords}",
        f"Date: {created_at}",
        "",
        "AI Career Feedback:"
    ]

    for line in details:
        pdf.drawString(50, y, line[:90])
        y -= 20

        if y < 50:
            pdf.showPage()
            y = height - 50
            pdf.setFont("Helvetica", 12)

    pdf.setFont("Helvetica", 10)

    for line in ai_feedback.split("\n"):
        if y < 50:
            pdf.showPage()
            y = height - 50
            pdf.setFont("Helvetica", 10)

        line = line.strip()

        while len(line) > 90:
            pdf.drawString(50, y, line[:90])
            line = line[90:]
            y -= 15

            if y < 50:
                pdf.showPage()
                y = height - 50
                pdf.setFont("Helvetica", 10)

        pdf.drawString(50, y, line)
        y -= 15

    pdf.save()
    buffer.seek(0)

    response = make_response(buffer.getvalue())
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = "attachment; filename=AI_Resume_Report.pdf"

    return response


@app.route("/mock_interview")
def mock_interview():
    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template(
        "interview.html",
        questions=interview_questions
    )


@app.route("/submit_interview", methods=["POST"])
def submit_interview():
    if "user_id" not in session:
        return redirect(url_for("login"))

    question = request.form["question"]
    answer = request.form["answer"]

    feedback = generate_interview_feedback(question, answer)

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO interviews (
            user_id,
            question,
            answer,
            feedback
        )
        VALUES (?, ?, ?, ?)
    """, (
        session["user_id"],
        question,
        answer,
        feedback
    ))

    conn.commit()
    conn.close()

    return render_template(
        "interview_result.html",
        question=question,
        answer=answer,
        feedback=feedback
    )


@app.route("/admin")
def admin_dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session["role"] != "admin":
        return "Access denied. Admin only."

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM results")
    total_results = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM interviews")
    total_interviews = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(ats_score) FROM results")
    avg_score_data = cursor.fetchone()
    average_score = round(avg_score_data[0], 2) if avg_score_data[0] else 0

    cursor.execute("""
        SELECT id, name, email, role
        FROM users
        ORDER BY id DESC
    """)
    users = cursor.fetchall()

    cursor.execute("""
        SELECT filename, job_role, ats_score, created_at
        FROM results
        ORDER BY created_at DESC
    """)
    results = cursor.fetchall()

    cursor.execute("""
        SELECT question, answer, feedback, created_at
        FROM interviews
        ORDER BY created_at DESC
    """)
    interviews = cursor.fetchall()

    cursor.execute("""
        SELECT job_role, COUNT(*)
        FROM results
        GROUP BY job_role
    """)
    role_data = cursor.fetchall()

    conn.close()

    return render_template(
        "admin.html",
        total_users=total_users,
        total_results=total_results,
        total_interviews=total_interviews,
        average_score=average_score,
        users=users,
        results=results,
        interviews=interviews,
        role_data=role_data
    )


@app.route("/make_admin")
def make_admin():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    email = "aaryapatil011@gmail.com"

    cursor.execute(
        "UPDATE users SET role = 'admin' WHERE email = ?",
        (email,)
    )

    conn.commit()
    conn.close()

    return "Admin updated successfully. Now logout and login again."



if __name__ == "__main__":
    app.run(debug=True)