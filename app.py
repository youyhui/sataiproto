from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_session import Session
from cs50 import SQL
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functions import generate_user_id, validEmail
from ai import generate_mcqs_by_topics
import os
import json
import re

# --- Flask setup ---
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = os.getenv('FLASK_SECRET', 'your_secret_key')
Session(app)

# --- Databases ---
db = SQL("sqlite:///data.db")         # users, questions, answers, performance, questionImages
qc = SQL("sqlite:///questions.db")    # optional separate for questionImages

# --- Load static JSON questions (backup) ---
def load_questions():
    with open('questions.json', 'r') as f:
        return json.load(f)['questions']

# --- Normalize answers ---
def normalize_answer(ans):
    if not ans: return ''
    ans = re.sub(r'\\\(|\\\)', '', ans)
    return ans.replace(' ', '').lower()

# --- Before each request ---
@app.before_request
def _init_session():
    session.setdefault('score', 0)
    session.setdefault('current_question', 0)
    session.setdefault('answers', [])

# --- Routes ---
@app.route('/', methods=['GET', 'POST'])
def index():
    # Serve quiz questions
    questions = load_questions()
    idx = session['current_question']
    if idx >= len(questions):
        return redirect(url_for('final_score'))
    q = questions[idx]
    if request.method == 'POST':
        user_ans = request.form.get('user_answer', '').strip()
        correct = q['correct_answer'].strip()
        is_corr = normalize_answer(user_ans) == normalize_answer(correct)
        if is_corr:
            session['score'] += 1
        session['answers'].append({
            'question': q['question'], 'user_answer': user_ans,
            'correct_answer': correct, 'is_correct': is_corr
        })
        session['current_question'] += 1
        return redirect(url_for('index'))
    return render_template('index.html', question=q, index=idx)

@app.route('/final_score')
def final_score():
    total = len(load_questions())
    return render_template('final_score.html', score=session['score'], total=total)

@app.route('/restart')
def restart():
    session.clear()
    return redirect(url_for('index'))

# --- Authentication & Dashboard ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('usr')
        pwd = request.form.get('pwd')
        if not user or not pwd or len(pwd) < 8:
            return "failure"
        userId = generate_user_id(user)
        row = db.execute("SELECT password_hash FROM users WHERE id = ?", userId)
        if row and check_password_hash(row[0]['password_hash'], pwd):
            session['userId'] = userId
            return redirect(url_for('dashboard'))
        return "Log In Failed"
    return render_template('index.html', username=None)

@app.route('/signup', methods=['POST'])
def signup():
    user = request.form.get('usr')
    email = request.form.get('email')
    pwd = request.form.get('pwd')
    if not user or not email or not pwd or len(pwd) < 8 or not validEmail(email):
        return "failure"
    userId = generate_user_id(user)
    hash_pw = generate_password_hash(pwd)
    db.execute("INSERT INTO users (id, username, email, password_hash) VALUES(?, ?, ?, ?)",
               userId, user, email, hash_pw)
    session['userId'] = userId
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# --- Question submission ---
@app.route('/questions', methods=['GET'])
def questions_page():
    return render_template('questions.html')

@app.route('/qregister', methods=['POST'])
def question_register():
    # handle form data... (omitted, same as existing code)
    return "success"

# --- Analyze weak topics & AI practice ---
def analyze_weak_topics(user_id):
    rows = db.execute("""
        SELECT category, SUM(CASE WHEN isCorrect=0 THEN 1 ELSE 0 END) AS wrong
        FROM performance JOIN questions ON performance.questionId = questions.id
        WHERE performance.userId = ?
        GROUP BY category ORDER BY wrong DESC LIMIT 3
    """, user_id)
    return [r['category'] for r in rows if r['wrong']]

@app.route('/ai_practice_ui')
def ai_practice_ui():
    if "userId" not in session:
        return redirect(url_for("login"))
    return render_template("ai_practice.html")

@app.route('/ai_practice', methods=['POST'])
def ai_practice():
    uid = session.get('userId')
    if not uid: return jsonify({'status':'fail','message':'Not logged in'}),401
    topics = analyze_weak_topics(uid)
    if not topics: return jsonify({'status':'fail','message':'No weak topics'}),404
    qs = generate_mcqs_by_topics(topics)
    return jsonify({'status':'success','questions': qs})

if __name__ == '__main__':
    app.run(debug=True)# --- FILE: ai.py ---

import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_mcqs_by_topics(topics, num_questions=5):
    prompt = f"""
You are a SAT MCQ generator. Generate {num_questions} SAT-style multiple-choice questions in the following categories: {', '.join(topics)}.

Format strictly like this (no extra commentary):
Question: <question text>
A. <option A>
B. <option B>
C. <option C>
D. <option D>
Correct Answer: <A/B/C/D>

One blank line between questions.
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return parse_mcqs(response.choices[0].message.content)
    except Exception as e:
        print("OpenAI error:", e)
        return []

def parse_mcqs(text):
    mcqs = []
    questions = text.strip().split("\n\n")
    for q in questions:
        lines = q.strip().split("\n")
        if len(lines) < 6:
            continue
        try:
            q_text = lines[0].replace("Question:", "").strip()
            options = {
                lines[1][0]: lines[1][3:].strip(),
                lines[2][0]: lines[2][3:].strip(),
                lines[3][0]: lines[3][3:].strip(),
                lines[4][0]: lines[4][3:].strip(),
            }
            correct = lines[5].replace("Correct Answer:", "").strip().upper()

            mcqs.append({
                "questionText": q_text,
                "options": options,
                "correctAnswer": correct,
                "explanation": "Generated using AI based on topic analysis."
            })
        except Exception as e:
            print("Parsing error:", e)
            continue
    return mcqs
