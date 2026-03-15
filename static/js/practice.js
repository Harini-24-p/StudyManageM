const fileInput = document.getElementById("answerSheet");
const fileNameDisplay = document.getElementById("fileName");

fileInput.addEventListener("change", function () {
    if (fileInput.files.length > 0) {
        fileNameDisplay.textContent = "Uploaded: " + fileInput.files[0].name;
    }
});

function evaluateTest() {

    const syllabusText = document.getElementById("syllabusText").value;
    const resultDiv = document.getElementById("result");

    if (fileInput.files.length === 0 || syllabusText.trim() === "") {
        alert("Upload PDF and enter syllabus text!");
        return;
    }

    const formData = new FormData();
    formData.append("answerSheet", fileInput.files[0]);
    formData.append("syllabusText", syllabusText);

    resultDiv.style.display = "block";
    resultDiv.innerHTML = "Evaluating using AI... ⏳";

    fetch("/evaluate", {
        method: "POST",
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        resultDiv.innerHTML = `
            <h3>Score: ${data.score}/100</h3>
            <p>${data.message}</p>
        `;
    })
    .catch(() => {
        resultDiv.innerHTML = "Error during evaluation!";
    });
}