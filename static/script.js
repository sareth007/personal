// Load events on page load
document.addEventListener("DOMContentLoaded", function() {
    loadEvents();
});

function loadEvents() {
    fetch("/api/events")
        .then(response => response.json())
        .then(data => {
            const grid = document.getElementById("eventsGrid");
            grid.innerHTML = "";
            data.forEach(event => {
                const card = document.createElement("div");
                card.className = "event-card";
                card.innerHTML = `
                    <h3>${event.title}</h3>
                    <p><strong>Date:</strong> ${event.date}</p>
                    <p>${event.description}</p>
                `;
                grid.appendChild(card);
            });
        })
        .catch(err => {
            console.error(err);
            document.getElementById("eventsGrid").innerHTML = "<p>Error loading events</p>";
        });
}

// Show add event modal (already in your HTML)
function showAddEventModal() {
    document.getElementById("addEventModal").style.display = "block";
}

function closeModal() {
    document.getElementById("addEventModal").style.display = "none";
}

// Submit new event
document.getElementById("addEventForm")?.addEventListener("submit", function(e) {
    e.preventDefault();

    const title = document.getElementById("eventTitle").value;
    const date = document.getElementById("eventDate").value;
    const description = document.getElementById("eventDescription").value;

    fetch("/api/events", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title, date, description })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === "success") {
            loadEvents(); // Refresh the events grid
            closeModal();
        } else {
            alert(data.message);
        }
    })
    .catch(err => console.error(err));
});
