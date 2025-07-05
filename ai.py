import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

def generate_mcqs_by_topics(topics, num_questions=5):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

    prompt = f"""
You are a SAT MCQ generator. Generate {num_questions} SAT-style multiple-choice questions in LaTeX format in the following categories: {', '.join(topics)}.

Format strictly like this (no extra commentary):
Question: <question text>
A. <option A>
B. <option B>
C. <option C>
D. <option D>
Correct Answer: <A/B/C/D>

One blank line between questions.
"""

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key,
    }

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        generated_text = (
            data.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "")
        )
        return parse_mcqs(generated_text)
    except Exception as e:
        print("Gemini API error:", e)
        return []

def parse_mcqs(text):
    mcqs = []
    questions = text.strip().split("\n\n")
    mcqs = []
    try:
            data = json.loads(text)
            for item in data.get('questions', []):
             mcqs.append({
                'questionText': item['question'],
                'options': {
                    'A': item['options'][0],
                    'B': item['options'][1],
                    'C': item['options'][2],
                    'D': item['options'][3]
                },
                'correctAnswer': item['correct_answer'][0]
            })
            return mcqs
    except:
            # Fallback to original parsing
            questions = text.strip().split("\n\n")
            for q in questions:
            # ... (original parsing code)
                return []
