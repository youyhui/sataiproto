from ai import generate_mcqs_by_topics

# Try topics you know are common
qs = generate_mcqs_by_topics(["Algebra", "Geometry"])

print("\n=== AI Response ===")
for i, q in enumerate(qs, 1):
    print(f"Q{i}: {q['questionText']}")
    for k, v in q['options'].items():
        print(f"  {k}: {v}")
    print(f"✅ Correct: {q['correctAnswer']}\n")
