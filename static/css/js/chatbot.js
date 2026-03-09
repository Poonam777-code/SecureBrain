let isProcessing = false;

function sendMessage() {

    if (isProcessing) return;

    const input = document.getElementById("chatInput");
    const chatBox = document.getElementById("chatMessages");
    const message = input.value.trim();

    if (!message) return;

    isProcessing = true;

    chatBox.style.display = "flex";
    chatBox.style.flexDirection = "column";

    addMessage("user-message", message);

    input.value = "";
    input.disabled = true;

    const botSpan = addMessage("bot-message", "Thinking...");

    fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: message })
    })
    .then(res => res.json())
    .then(data => {
        botSpan.textContent = data.response;
    })
    .catch(() => {
        botSpan.textContent = "Error.";
    })
    .finally(() => {
        input.disabled = false;
        input.focus();
        isProcessing = false;
        chatBox.scrollTop = chatBox.scrollHeight;
    });
}

function handleKey(e) {
    if (e.key === "Enter") {
        sendMessage();
    }
}

function addMessage(className, text) {

    const chatBox = document.getElementById("chatMessages");

    const div = document.createElement("div");
    div.className = className;

    div.style.width = "100%";
    div.style.marginBottom = "12px";
    div.style.clear = "both";

    const span = document.createElement("span");
    span.textContent = text;

    div.appendChild(span);
    chatBox.appendChild(div);

    chatBox.scrollTop = chatBox.scrollHeight;

    return span;
}