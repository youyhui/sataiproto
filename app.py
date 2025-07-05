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
from dotenv import load_dotenv

load_dotenv()

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
    
    # Generate questions directly
    topics = analyze_weak_topics(session['userId'])
    questions = generate_mcqs_by_topics(topics) if topics else []
    return render_template("ai_practice.html", questions=questions)

# Remove /ai_practice route (no longer needed)

if __name__ == '__main__':
    app.run(debug=True)