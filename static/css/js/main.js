function openChat() {
    document.getElementById("chatModal").style.display = "block";
}

function closeChat() {
    document.getElementById("chatModal").style.display = "none";
}

function handleKey(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
}

function sendMessage() {

    let input = document.getElementById("chatInput");
    let message = input.value.trim();

    if (!message) return;

    let chatBox = document.getElementById("chatMessages");

    chatBox.innerHTML += `
        <div class="user-message">
            <span>${message}</span>
        </div>
    `;

    input.value = "";
    chatBox.scrollTop = chatBox.scrollHeight;

    fetch("/chat", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({query: message})
    })
    .then(res => res.json())
    .then(data => {

        chatBox.innerHTML += `
            <div class="bot-message">
                <span>${data.response}</span>
            </div>
        `;

        chatBox.scrollTop = chatBox.scrollHeight;
    })
    .catch(err => {
        chatBox.innerHTML += `
            <div class="bot-message">
                <span>⚠ Error connecting to AI</span>
            </div>
        `;
    });
}

/////////////////////////////////////////////////////////////
// ✅ NEW FUNCTION FOR URL SAFETY (OPENS NEW PAGE)
/////////////////////////////////////////////////////////////

function openUrlCheckPage() {

    let input = document.getElementById("searchInput");

    if (!input) {
        alert("Search input not found.");
        return;
    }

    let url = input.value.trim();

    if (!url) {
        alert("Please enter a URL first.");
        return;
    }

    // Redirect to new validation page
    window.location.href = "/url-check?target=" + encodeURIComponent(url);
}