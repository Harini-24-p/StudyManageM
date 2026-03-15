// ===============================
// GLOBAL VARIABLES
// ===============================
let questions = [];
let currentQuestionIndex = 0;
let score = 0;
let timerInterval;
let timeLeft = 30;

// ===============================
// GENERATE QUIZ FROM AI
// ===============================
function generateQuiz() {
    const fileInput = document.getElementById("syllabusFile");
    const file = fileInput.files[0];

    if (!file) {
        alert("Please upload a syllabus file!");
        return;
    }

    let formData = new FormData();
    formData.append("syllabus", file);

    fetch("/generate_ai_quiz", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        questions = data.questions;
        document.querySelector(".upload-card").style.display = "none";
        document.getElementById("quizSection").style.display = "block";
        startQuiz();
    })
    .catch(error => {
        console.error("Error:", error);
    });
}

// ===============================
// START QUIZ
// ===============================
function startQuiz() {
    currentQuestionIndex = 0;
    score = 0;
    showQuestion();
}

// ===============================
// SHOW QUESTION
// ===============================
function showQuestion() {
    resetTimer();

    const questionElement = document.querySelector(".question");
    const choicesElement = document.querySelector(".choices");

    let currentQuestion = questions[currentQuestionIndex];

    questionElement.innerText = currentQuestion.question;
    choicesElement.innerHTML = "";

    currentQuestion.choices.forEach((choice, index) => {
        let button = document.createElement("button");
        button.innerText = choice;
        button.onclick = () => selectAnswer(index);
        choicesElement.appendChild(button);
    });

    startTimer();
}

// ===============================
// TIMER
// ===============================
function startTimer() {
    timeLeft = 30;
    const timerElement = document.querySelector(".timer");
    timerElement.innerText = "⏳ " + timeLeft + "s";

    timerInterval = setInterval(() => {
        timeLeft--;
        timerElement.innerText = "⏳ " + timeLeft + "s";

        if (timeLeft <= 0) {
            clearInterval(timerInterval);
            nextQuestion();
        }
    }, 1000);
}

function resetTimer() {
    clearInterval(timerInterval);
}

// ===============================
// SELECT ANSWER
// ===============================
function selectAnswer(selectedIndex) {
    resetTimer();

    if (selectedIndex === questions[currentQuestionIndex].answer) {
        score++;
    }

    nextQuestion();
}

// ===============================
// NEXT QUESTION
// ===============================
function nextQuestion() {
    currentQuestionIndex++;

    if (currentQuestionIndex < questions.length) {
        showQuestion();
    } else {
        endQuiz();
    }
}

// ===============================
// END QUIZ
// ===============================
function endQuiz() {
    const quizSection = document.getElementById("quizSection");
    const scoreCard = document.querySelector(".scoreCard");

    let totalMarks = questions.length;
    let percentage = ((score / totalMarks) * 100).toFixed(2);

    scoreCard.innerHTML = 
        "🎉 Final Score: " + score + " / " + totalMarks +
        "<br>📊 Percentage: " + percentage + "%";

    // Send score to Flask backend
    fetch("/submit_quiz", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: "score=" + score + "&total_marks=" + totalMarks
    });

    document.querySelector(".choices").innerHTML = "";
    document.querySelector(".question").innerHTML = "Quiz Completed!";
}