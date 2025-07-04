import requests
import os
from dotenv import load_dotenv

API_KEY = os.getenv("GEMINI_API_KEY")
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = "us-central1"  # adjust if needed
MODEL_ID = "gemini-2.5"   # replace with your Gemini model name

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

    url = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/{MODEL_ID}:generateText"

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": API_KEY,
    }

    payload = {
        "prompt": prompt,
        "temperature": 0.7,
        "maxOutputTokens": 1000,
        "topP": 0.95,
        "topK": 40,
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        generated_text = data.get("candidates", [{}])[0].get("content", "")
        return parse_mcqs(generated_text)
    except Exception as e:
        print("Gemini API error:", e)
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
