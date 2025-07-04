async function practiceWithAI() {
    const response = await fetch('/ai_practice', {
        method: 'POST'
    });
    const data = await response.json();
    const output = document.getElementById('ai-output');
    output.innerHTML = '';
    if (data.status === 'success') {
        data.questions.forEach((q, idx) => {
            const card = document.createElement('div');
            card.className = 'card';
            card.innerHTML = `
                <h4>Q${idx + 1}: ${q.questionText}</h4>
                <ul>
                    ${Object.entries(q.options)
                        .map(([key, val]) => `<li><strong>${key}:</strong> ${val}</li>`)
                        .join('')}
                </ul>
                <p><strong>Answer:</strong> ${q.correctAnswer}</p>
            `;
            output.appendChild(card);
        });
    } else {
        output.innerHTML = `<p>${data.message}</p>`;
    }
}