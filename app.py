from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import os
from werkzeug.utils import secure_filename
from openai import OpenAI
import json
from flask import jsonify, request, session

client = OpenAI(api_key="YOUR_API_KEY")

app = Flask(__name__)
app.secret_key = "secret123"

# ================= UPLOAD FOLDER =================
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Create folder if not exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ================= DATABASE =================
DB_NAME = "database.db"

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            names TEXT NOT NULL,
            surnames TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS question_papers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT,
            year TEXT,
            filename TEXT,
            generated_questions TEXT
        )
    """)
    

    conn.execute("""
        CREATE TABLE IF NOT EXISTS quiz_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            score INTEGER,
            total_marks INTEGER,
            percentage REAL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS login_activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()

init_db()

# ================= INDEX =================
@app.route("/")
def index():
    return render_template("index.html")

# ================= REGISTER =================
@app.route("/register", methods=["POST"])
def register():
    names = request.form.get("names")
    surnames = request.form.get("surnames")
    email = request.form.get("email")
    password = request.form.get("password")

    if not names or not surnames or not email or not password:
        flash("All fields are required")
        return redirect(url_for("index"))

    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO users (names, surnames, email, password) VALUES (?, ?, ?, ?)",
            (names, surnames, email, password)
        )
        conn.commit()
        flash("Registration successful! Please login.")
    except sqlite3.IntegrityError:
        flash("Email already exists!")
    finally:
        conn.close()

    return redirect(url_for("index"))

# ================= LOGIN =================
@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")

    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE email=? AND password=?",
        (email, password)
    ).fetchone()

    if user:
        session["user_id"] = user["id"]
        session["user_name"] = user["names"]

        # ✅ STORE LOGIN ACTIVITY
        conn.execute(
            "INSERT INTO login_activity (user_id) VALUES (?)",
            (user["id"],)
        )
        conn.commit()
        conn.close()

        return redirect(url_for("dashboard"))
    else:
        conn.close()
        flash("Invalid email or password")
        return redirect(url_for("index"))

# ================= DASHBOARD =================
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("index"))
    return render_template("dashboard.html", name=session["user_name"])

# ================= DASHBOARD ROUTES =================

# ================= QUESTION BANK PAGE =================
@app.route("/question-bank")
def question_bank():
    if "user_id" not in session:
        return redirect(url_for("index"))

    search_query = request.args.get("search")

    conn = get_db()

    if search_query:
        papers = conn.execute(
            "SELECT * FROM question_papers WHERE subject LIKE ? ORDER BY id DESC",
            ('%' + search_query + '%',)
        ).fetchall()
    else:
        papers = conn.execute(
            "SELECT * FROM question_papers ORDER BY id DESC"
        ).fetchall()

    conn.close()

    return render_template("question-bank.html", papers=papers)


# ================= UPLOAD PAPER =================
@app.route("/upload-paper", methods=["POST"])
def upload_paper():
    if "user_id" not in session:
        return redirect(url_for("index"))

    file = request.files.get("file")
    subject = request.form.get("subject")
    year = request.form.get("year")

    if not file or not subject or not year:
        flash("All fields are required!", "error")
        return redirect(url_for("question_bank"))

    # 🔥 secure filename (important)
    filename = secure_filename(file.filename)

    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(file_path)

    conn = get_db()
    conn.execute("""
        INSERT INTO question_papers (subject, year, filename)
        VALUES (?, ?, ?)
    """, (subject, year, filename))

    conn.commit()
    conn.close()

    flash("Question paper uploaded successfully!", "success")
    return redirect(url_for("question_bank"))

# ================= DELETE PAPER =================
@app.route("/delete/<int:paper_id>")
def delete_paper(paper_id):
    if "user_id" not in session:
        return redirect(url_for("index"))

    conn = get_db()

    paper = conn.execute(
        "SELECT * FROM question_papers WHERE id = ?",
        (paper_id,)
    ).fetchone()

    if paper:
        # Delete file from uploads folder
        if paper["filename"]:
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], paper["filename"])
            if os.path.exists(file_path):
                os.remove(file_path)

        # Delete from database
        conn.execute(
            "DELETE FROM question_papers WHERE id = ?",
            (paper_id,)
        )
        conn.commit()

        flash("Question paper deleted successfully!", "success")
    else:
        flash("Paper not found!", "error")

    conn.close()
    return redirect(url_for("question_bank"))

# ================= QUIZ =================
@app.route("/quizz")
def quiz():
    if "user_id" not in session:
        return redirect(url_for("index"))
    return render_template("quizz.html")


import os
import re
import random
from collections import Counter
from flask import jsonify, request, session
import PyPDF2


# ================= GENERATE AI QUIZ =================
@app.route("/generate_ai_quiz", methods=["POST"])
def generate_ai_quiz():

    if "user_id" not in session:
        return jsonify({"error": "Login required"}), 401

    file = request.files.get("syllabusFile")

    if not file:
        return jsonify({"error": "Upload syllabus file"}), 400

    upload_folder = "static/uploads"
    os.makedirs(upload_folder, exist_ok=True)

    filepath = os.path.join(upload_folder, file.filename)
    file.save(filepath)

    syllabus_text = ""

    # ===== Extract text =====
    if file.filename.endswith(".pdf"):

        with open(filepath, "rb") as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)

            for page in reader.pages:
                text = page.extract_text()

                if text:
                    syllabus_text += text

    else:

        with open(filepath, "r", encoding="utf-8") as f:
            syllabus_text = f.read()


    # ===== Clean text =====
    syllabus_text = syllabus_text.lower()
    syllabus_text = re.sub(r'[^a-zA-Z ]', '', syllabus_text)

    words = syllabus_text.split()

    stop_words = [
        "the","is","are","of","and","to","in","a","an","for",
        "with","on","that","this","by","as","at","from","or"
    ]

    filtered_words = [w for w in words if w not in stop_words and len(w) > 4]

    word_freq = Counter(filtered_words)

    keywords = [w for w, f in word_freq.most_common(40)]

    if len(keywords) < 4:
        return jsonify({"error": "Not enough content"}), 400


    # ===== Generate questions =====
    quiz_data = []

    question_templates = [

        "Which of the following best describes {}?",
        "What is the primary purpose of {} in computing?",
        "In modern technology, how is {} mainly used?",
        "Which concept is most closely related to {}?",
        "Why is {} important in computer science?",
        "Which field commonly uses {}?",
        "What role does {} play in information technology?"

    ]

    for i in range(10):

        main_word = random.choice(keywords)

        template = random.choice(question_templates)

        question = template.format(main_word.capitalize())

        correct_answer = main_word.capitalize()

        wrong = random.sample(
            [w.capitalize() for w in keywords if w != main_word], 3
        )

        options = wrong + [correct_answer]

        random.shuffle(options)

        letters = ["A","B","C","D"]

        option_dict = {}
        correct_letter = ""

        for j, opt in enumerate(options):

            option_dict[letters[j]] = opt

            if opt == correct_answer:
                correct_letter = letters[j]

        quiz_data.append({
            "question": question,
            "options": option_dict,
            "answer": correct_letter
        })


    # ===== Save to session =====
    session["quiz_questions"] = quiz_data
    session["current_question"] = 0
    session["score"] = 0


    if not quiz_data:
        return jsonify({"error": "Quiz could not be generated"}), 400


    return jsonify({
        "question": quiz_data[0]
    })


# ================= NEXT QUESTION =================
@app.route("/next_question", methods=["POST"])
def next_question():

    data = request.json
    selected = data.get("selected_answer")

    questions = session["quiz_questions"]
    index = session["current_question"]

    correct = questions[index]["answer"]

    if selected == correct:
        session["score"] += 1

    index += 1
    session["current_question"] = index

    if index >= len(questions):

        return jsonify({
            "finished": True,
            "score": session["score"],
            "total": len(questions)
        })

    return jsonify({
        "question": questions[index]
    })

@app.route("/practice")
def practice():
    if "user_id" not in session:
        return redirect(url_for("index"))
    return render_template("practice.html")

from flask import request, jsonify
import PyPDF2
import os
@app.route("/evaluate", methods=["POST"])
def evaluate():

    file = request.files.get("answerSheet")
    syllabus_text = request.form.get("syllabusText")

    if not file or not syllabus_text:
        return jsonify({"error": "Missing data"}), 400

    # Save uploaded file safely
    upload_folder = "static/uploads"
    os.makedirs(upload_folder, exist_ok=True)
    filepath = os.path.join(upload_folder, file.filename)
    file.save(filepath)

    # ==============================
    # Extract PDF Text
    # ==============================
    pdf_text = ""

    try:
        with open(filepath, "rb") as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    pdf_text += text
    except Exception as e:
        return jsonify({"error": "Error reading PDF"}), 500

    pdf_text = pdf_text.lower()
    syllabus_text = syllabus_text.lower()

    answer_words = pdf_text.split()
    topic_keywords = syllabus_text.split()

    # Prevent division by zero
    if len(topic_keywords) == 0:
        return jsonify({"error": "No syllabus keywords provided"}), 400

    if len(answer_words) == 0:
        return jsonify({"error": "Empty answer sheet"}), 400

    # ==============================
    # RULE 1: Topic Relevance Score
    # ==============================
    match_count = 0
    for word in topic_keywords:
        if word in pdf_text:   # better than checking in split list
            match_count += 1

    relevance_percentage = (match_count / len(topic_keywords)) * 100

    # ==============================
    # RULE 2: Concept Density
    # ==============================
    topic_word_count = 0
    for word in answer_words:
        if word in topic_keywords:
            topic_word_count += 1

    density = (topic_word_count / len(answer_words)) * 100

    # ==============================
    # RULE 3: Final Scoring Logic
    # ==============================

    # Mostly unrelated
    if relevance_percentage < 30:
        final_score = 20
        message = "Answer is mostly unrelated to the topic ❌"

    # Perfect match (all keywords found)
    elif match_count == len(topic_keywords):
        final_score = 100
        message = "Perfect Answer! Fully relevant ✅"

    # Normal scoring
    else:
        final_score = int((relevance_percentage * 0.7) + (density * 0.3))

        if final_score >= 75:
            message = "Answer is highly relevant to the topic ✅"
        elif final_score >= 50:
            message = "Answer is moderately relevant 👍"
        else:
            message = "Answer is partially related ⚠️"

    # Limit score to 100
    if final_score > 100:
        final_score = 100

    return jsonify({
        "score": final_score,
        "relevance_percentage": round(relevance_percentage, 2),
        "concept_density": round(density, 2),
        "message": message
    })

@app.route("/study-planner")
def study_planner():
    if "user_id" not in session:
        return redirect(url_for("index"))
    return render_template("study-planner.html")
# ================= PERFORMANCE PAGE =================
@app.route("/performance")
def performance():
    if "user_id" not in session:
        return redirect(url_for("index"))

    return render_template("performance.html")

# ================= WEEKLY PERFORMANCE DATA =================
@app.route("/performance_data")
def performance_data():

    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = session["user_id"]

    conn = get_db()

    # Quiz scores for last 7 days
    quiz_scores = conn.execute("""
        SELECT 
            date(date) as day,
            percentage
        FROM quiz_results
        WHERE user_id = ?
        AND date >= date('now','-7 days')
        ORDER BY date
    """, (user_id,)).fetchall()


    # Login count for last 7 days
    login_counts = conn.execute("""
        SELECT 
            date(login_time) as day,
            COUNT(*) as login_count
        FROM login_activity
        WHERE user_id = ?
        AND login_time >= date('now','-7 days')
        GROUP BY day
        ORDER BY day
    """, (user_id,)).fetchall()


    conn.close()

    return jsonify({
        "quiz_scores": [dict(row) for row in quiz_scores],
        "login_counts": [dict(row) for row in login_counts]
    })

@app.route("/create-question-paper")
def create_question_paper():
    if "user_id" not in session:
        return redirect(url_for("index"))
    return render_template("create-question-paper.html")

#============ create question paper =============#
import os
from werkzeug.utils import secure_filename




@app.route("/generate", methods=["POST"])
def generate():
    if "user_id" not in session:
        return redirect(url_for("index"))

    file = request.files.get("syllabus")
    difficulty = request.form.get("difficulty")

    if not file or not difficulty:
        return redirect(url_for("create_question_paper"))

    # Secure filename
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    # Save file
    file.save(filepath)

    # ---------------------------
    # Extract Text From File
    # ---------------------------
    syllabus_text = ""

    try:
        if filename.endswith(".txt"):
            with open(filepath, "r", encoding="utf-8") as f:
                syllabus_text = f.read()

        elif filename.endswith(".pdf"):
            with open(filepath, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        syllabus_text += text

        else:
            syllabus_text = "Syllabus uploaded."

    except Exception as e:
        syllabus_text = "Could not extract syllabus content."

    # ---------------------------
    # Generate Questions
    # ---------------------------

    if difficulty == "Easy":
        questions = f"""
UNIVERSITY EXAMINATION

SECTION A (2 Marks)
1. Define key concepts from syllabus.
2. List important terms.
3. Write short notes on main topics.

SECTION B (5 Marks)
4. Explain core concepts briefly.
5. Discuss applications.

Based on Syllabus:
{syllabus_text[:500]}
"""

    elif difficulty == "Medium":
        questions = f"""
UNIVERSITY EXAMINATION

SECTION A (2 Marks)
1. Define important concepts.
2. Short notes on major topics.

SECTION B (5 Marks)
3. Explain topic in detail.
4. Compare related concepts.

SECTION C (10 Marks)
5. Discuss with examples.

Based on Syllabus:
{syllabus_text[:800]}
"""

    elif difficulty == "Hard":
        questions = f"""
UNIVERSITY EXAMINATION

SECTION A (5 Marks)
1. Analyze key concepts.
2. Compare theoretical approaches.

SECTION B (10 Marks)
3. Discuss advanced applications.
4. Solve analytical problems.

SECTION C (15 Marks)
5. Justify answers with detailed explanation.

Based on Syllabus:
{syllabus_text[:1000]}
"""

    else:
        questions = "Please select difficulty level."

    # ---------------------------
    # Save to Database
    # ---------------------------

    conn = get_db()
    conn.execute("""
        INSERT INTO question_papers (subject, year, filename, generated_questions)
        VALUES (?, ?, ?, ?)
    """, ("Generated Paper", difficulty, filename, questions))

    conn.commit()
    conn.close()

    # ---------------------------
    # Return Same Page With Output
    # ---------------------------

    return render_template(
        "create-question-paper.html",
        questions=questions
    )
# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)