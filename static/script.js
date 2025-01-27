let uuid_href = window.location.href

function createGrid(gridElement, isClickable) {
    gridElement.style.display = "grid";
    gridElement.style.gridTemplateColumns = `repeat(${GRID_SIZE}, 75px)`;
    gridElement.style.gridTemplateRows = `repeat(${GRID_SIZE}, 75px)`;

    for (let i = 0; i < GRID_SIZE; i++) {
        for (let j = 0; j < GRID_SIZE; j++) {
            const cell = document.createElement("div");
            cell.className = "cell";
            cell.dataset.x = i;
            cell.dataset.y = j;

            // Allow user to toggle ship placement
            if (isClickable) {
                cell.addEventListener("click", () => {
                    cell.classList.toggle("ship"); // Toggle ship color
                });
            }

            gridElement.appendChild(cell);
        }
    }
}
async function fetchMessages() {
    try {
        const response = await fetch('/get-all-messages');
        if (!response.ok) throw new Error('Failed to fetch messages');
        const data = await response.json();

        const messagesContainer = document.getElementById('messages');
        messagesContainer.innerHTML = ''; // Clear old messages

        data.forEach(msg => {
            const div = document.createElement('div');
            div.className = 'message';
            div.innerHTML = `<span class="username">${msg.username}:</span> <span class="text">${msg.text}</span>`;
            messagesContainer.appendChild(div);
        });

        // Auto-scroll to the bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    } catch (error) {
        console.error('Error fetching messages:', error);
    }
}


async function fetchStates() {
    try {
        const response = await fetch('/get-state/' + uuid_href);
        if (!response.ok) throw new Error('Failed to fetch messages');
        const state = await response.json();

        const messagesContainer = document.getElementById('messages');
        messagesContainer.innerHTML = ''; // Clear old messages

        data.forEach(msg => {
            const div = document.createElement('div');
            div.className = 'message';
            div.innerHTML = `<span class="username">${msg.username}:</span> <span class="text">${msg.text}</span>`;
            messagesContainer.appendChild(div);
        });

        // Auto-scroll to the bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    } catch (error) {
        console.error('Error fetching messages:', error);
    }
}

// Fetch messages every 2 seconds

// Initialize the grid and listen for the submit action
const GRID_SIZE = 5; // Define grid size (e.g., 5x5)
const userGrid = document.getElementById("user-grid");
createGrid(userGrid, true);



document.getElementById("submit-layout").addEventListener("click", () => {
    const selectedCells = [];
    document.querySelectorAll(".cell.ship").forEach((cell) => {
        selectedCells.push({
            x: parseInt(cell.dataset.x),
            y: parseInt(cell.dataset.y),
        });
    });

    if (selectedCells.length === 0) {
        alert("You must place at least one ship before submitting!");
        return;
    }

    // Send the ship layout to the server
    fetch("/submit-ships", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ ships: selectedCells, uuid: uuid_href}),
    })
        .then((response) => {
            if (!response.ok) {
                throw new Error("Failed to submit ship layout");
            }
            return response.json();
        })
        .then((data) => {
            alert("Ship layout submitted successfully!");
            console.log("Server response:", data);
            window.location.reload();
        })
        .catch((error) => {
            alert("An error occurred while submitting your ship layout.");
            console.error("Error:", error);
        });
});
