# --- FILE: ai.py ---

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
                "explanation": "Click to reveal explanation..."
            })
        except Exception as e:
            print("Parsing error:", e)
            continue
    return mcqs
