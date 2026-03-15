const paperView = document.getElementById("paperView");
const chatBox = document.getElementById("chatBox");
const chatBody = document.getElementById("chatBody");
const chatInput = document.getElementById("chatInput");

function generatePaper() {
  const difficulty = document.getElementById("difficulty").value;

  paperView.innerHTML = `
    <div class="paper">
      <h2>Computer Science – Question Paper</h2>
      <div class="meta">
        Duration: 3 Hours | Max Marks: 100 | Difficulty: ${difficulty}
      </div>

      <h3>Section A (Short Answer)</h3>
      <ul>
        <li>Define Operating System. (5)</li>
        <li>What is an algorithm? (5)</li>
      </ul>

      <h3>Section B (Medium Answer)</h3>
      <ul>
        <li>Explain process scheduling. (10)</li>
        <li>Describe DBMS architecture. (10)</li>
      </ul>

      <h3>Section C (Long Answer)</h3>
      <ul>
        <li>Explain memory management techniques. (20)</li>
        <li>Discuss computer networks with diagram. (20)</li>
      </ul>
    </div>
  `;
}

function toggleChat() {
  chatBox.style.display = chatBox.style.display === "flex" ? "none" : "flex";
}

function sendMessage() {
  if (!chatInput.value) return;

  const user = document.createElement("div");
  user.className = "user-msg";
  user.innerText = chatInput.value;
  chatBody.appendChild(user);

  setTimeout(() => {
    const bot = document.createElement("div");
    bot.className = "bot-msg";
    bot.innerText =
      "🤖 I can generate difficulty-based questions from uploaded syllabus.";
    chatBody.appendChild(bot);
    chatBody.scrollTop = chatBody.scrollHeight;
  }, 600);

  chatInput.value = "";
}
