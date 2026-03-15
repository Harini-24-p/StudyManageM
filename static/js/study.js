// Load tasks from localStorage
let tasks = JSON.parse(localStorage.getItem("tasks")) || [];

const inputBox = document.getElementById("inputBox");
const addBtn = document.getElementById("addBtn");
const todoList = document.getElementById("todoList");
const completedCount = document.getElementById("completedCount");
const totalCount = document.getElementById("totalCount");
const progressFill = document.getElementById("progressFill");
const taskDate = document.getElementById("taskDate");

// Add button event
addBtn.addEventListener("click", addTask);

// Add task
function addTask() {
    const text = inputBox.value.trim();
    const date = taskDate.value;

    if (text === "") return;

    tasks.push({
        text: text,
        date: date,
        completed: false
    });

    inputBox.value = "";
    taskDate.value = "";

    saveData();
    displayTasks();
}

// Display tasks
function displayTasks() {
    todoList.innerHTML = "";

    let completed = 0;

    tasks.forEach((task, index) => {

        if (task.completed) completed++;

        const li = document.createElement("li");
        li.classList.add("task-item");

        li.innerHTML = `
            <span class="${task.completed ? 'completed' : ''}">
                ${task.text} ${task.date ? "(" + task.date + ")" : ""}
            </span>

            <div class="task-buttons">
                <button onclick="editTask(${index})">Edit</button>

                <button onclick="completeTask(${index})"
                    ${task.completed ? "disabled" : ""}>
                    ${task.completed ? "Completed" : "Complete"}
                </button>

                <button onclick="deleteTask(${index})">Delete</button>
            </div>
        `;

        todoList.appendChild(li);
    });

    totalCount.textContent = tasks.length;
    completedCount.textContent = completed;

    updateProgress(completed);
}

// Edit task
function editTask(index) {
    const newText = prompt("Edit task:", tasks[index].text);
    if (newText !== null && newText.trim() !== "") {
        tasks[index].text = newText.trim();
        saveData();
        displayTasks();
    }
}

// Complete task
function completeTask(index) {
    if (!tasks[index].completed) {
        tasks[index].completed = true;
        saveData();
        displayTasks();
    }
}

// Delete task
function deleteTask(index) {
    tasks.splice(index, 1);
    saveData();
    displayTasks();
}

// Update progress bar
function updateProgress(completed) {
    let percent = tasks.length === 0 ? 0 : (completed / tasks.length) * 100;
    progressFill.style.width = percent + "%";
}

// Save to localStorage
function saveData() {
    localStorage.setItem("tasks", JSON.stringify(tasks));
}

// Initial display
displayTasks();