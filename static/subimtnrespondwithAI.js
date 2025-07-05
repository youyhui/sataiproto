function goToQuestions() {
    window.location.href = "{{ url_for('questions.html') }}";  //add that question submitting utl
  }

async function practiceWithAI() {
  const output = document.getElementById("ai-output");
  output.innerHTML = "<div class='alert alert-info'> Generating questions...</div>";

  try {
    const response = await fetch("/ai_practice", {
      method: "POST",
      headers: { "Content-Type": "application/json" }
    });

    const result = await response.json();

    if (result.status === "success") {
      let html = "";
      result.questions.forEach((q, i) => {
        html += `
          <div class="card mb-4 p-3 shadow-sm">
            <h5>Q${i + 1}. ${q.questionText}</h5>
            <ul class="list-group mt-2">
              ${Object.entries(q.options).map(
                ([key, val]) => `<li class="list-group-item">${key}. ${val}</li>`
              ).join("")}
            </ul>
            <p class="mt-3"><strong>✅ Correct Answer: ${q.correctAnswer}</strong></p>
          </div>`;
      });
      output.innerHTML = html;
    } else {
      output.innerHTML = `<div class="alert alert-warning">⚠️ ${result.message}</div>`;
    }
  } catch (error) {
    console.error("Error:", error);
    output.innerHTML = "<div class='alert alert-danger'>❌ Error generating questions.</div>";
  }
}
