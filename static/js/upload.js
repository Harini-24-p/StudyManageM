let countdown;

function setMood(mood) {

    document.body.className = mood;

    const resultBox = document.getElementById("resultBox");
    const aiThinking = document.getElementById("aiThinking");
    const recommendations = document.getElementById("recommendations");

    const subject = document.getElementById("subject");
    const difficulty = document.getElementById("difficulty");
    const strategy = document.getElementById("strategy");
    const quote = document.getElementById("quote");

    resultBox.style.display = "block";
    recommendations.style.display = "none";
    aiThinking.style.display = "block";

    localStorage.setItem("selectedMood", mood);
    storeMoodHistory(mood);

    setTimeout(() => {

        let time;

        if (mood === "focused") {
            subject.innerText = "Advanced Python & Problem Solving";
            difficulty.innerText = "HARD";
            strategy.innerText = "Attempt a timed mock test (30 mins)";
            quote.innerText = "You're in peak mode. Push limits!";
            time = 30;
        }

        else if (mood === "tired") {
            subject.innerText = "Basic Concept Revision";
            difficulty.innerText = "EASY";
            strategy.innerText = "Short 15 min learning session";
            quote.innerText = "Small progress is still progress.";
            time = 60;
        }

        else if (mood === "stressed") {
            subject.innerText = "Light Practice & Review";
            difficulty.innerText = "EASY";
            strategy.innerText = "Slow reading + 5 MCQs";
            quote.innerText = "Calm mind learns faster.";
            time = 90;
        }

        else if (mood === "motivated") {
            subject.innerText = "Mixed Practice Test";
            difficulty.innerText = "MEDIUM";
            strategy.innerText = "Pomodoro 25+5 technique";
            quote.innerText = "Momentum creates mastery!";
            time = 45;
        }

        aiThinking.style.display = "none";
        recommendations.style.display = "block";

        document.querySelectorAll(".card").forEach((card, index) => {
            setTimeout(() => {
                card.classList.add("show");
            }, index * 300);
        });

        startTimer(time);
        showMostFrequentMood();

    }, 1500);
}

function startTimer(seconds) {

    clearInterval(countdown);

    let timeLeft = seconds;
    const timerDisplay = document.getElementById("timer");
    const progress = document.getElementById("progress");
    const totalLength = 377;

    countdown = setInterval(() => {

        timerDisplay.innerText = timeLeft;

        let offset = totalLength - (timeLeft / seconds) * totalLength;
        progress.style.strokeDashoffset = offset;

        timeLeft--;

        if (timeLeft < 0) {
            clearInterval(countdown);
            timerDisplay.innerText = "Start!";
        }

    }, 1000);
}

/* ================= MOOD ANALYTICS ================= */

function storeMoodHistory(mood) {
    let moods = JSON.parse(localStorage.getItem("moodHistory")) || [];
    moods.push(mood);
    localStorage.setItem("moodHistory", JSON.stringify(moods));
}

function showMostFrequentMood() {
    let moods = JSON.parse(localStorage.getItem("moodHistory")) || [];

    if (moods.length === 0) return;

    let count = {};
    moods.forEach(m => count[m] = (count[m] || 0) + 1);

    let mostMood = Object.keys(count).reduce((a, b) =>
        count[a] > count[b] ? a : b
    );

    document.getElementById("mostMood").innerText =
        mostMood.charAt(0).toUpperCase() + mostMood.slice(1);
}