/* ================= CHAT MODAL FUNCTIONS ================= */
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

    // User message
    chatBox.innerHTML += `
        <div class="user-message">
            <span>${message}</span>
        </div>
    `;
    input.value = "";
    chatBox.scrollTop = chatBox.scrollHeight;

    // AI response
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

/* ================= URL SAFETY CHECK ================= */
function openUrlCheckPage() {
    let input = document.getElementById("searchInput");
    if(!input){
        alert("Search input not found.");
        return;
    }
    let url = input.value.trim();
    if(!url){
        alert("Please enter a URL first.");
        return;
    }
    window.location.href = "/url-check?target=" + encodeURIComponent(url);
}

/* ================= MAIN SEARCH ================= */
function handleSearch() {
    let query = document.getElementById("searchInput").value.trim();
    if(!query){
        alert("Please enter something to search");
        return;
    }

    let resultsDiv = document.getElementById("results");
    resultsDiv.innerHTML = "<p>🔍 Searching...</p>";

    let isURL = query.includes(".") && !query.includes(" ");
    if(isURL){
        window.location.href = "/url-check?target=" + encodeURIComponent(query);
        return;
    }

    fetch("/smart-search", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ query: query })
    })
    .then(res => res.json())
    .then(data => {
        if(data.type === "answer"){
            showAnswer(data.response);
        } else {
            fetchSecureResults(query);
        }
    })
    .catch(() => {
        resultsDiv.innerHTML = "<p>❌ Search failed</p>";
    });
}

/* ================= AI ANSWER ================= */
function showAnswer(answer){
    let resultsDiv = document.getElementById("results");
    resultsDiv.innerHTML = `
        <div style="background:#fff; padding:20px; border-radius:12px;">
            <h3>🤖 AI Answer</h3>
            <p>${answer}</p>
        </div>
    `;
}

/* ================= SECURE SEARCH RESULTS ================= */
function fetchSecureResults(query) {
    let resultsDiv = document.getElementById("results");
    resultsDiv.innerHTML = "<p>🔍 Loading results...</p>";

    fetch("/secure-search", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ query: query })
    })
    .then(res => res.json())
    .then(data => {
        resultsDiv.innerHTML = "";

        if(!data || !data.results || data.results.length === 0){
            resultsDiv.innerHTML = "<p>No results found</p>";
            return;
        }

        // ⭐ TOP RESULT
        let top = data.results[0];
        resultsDiv.innerHTML += `
            <div class="top-result fade-in">
                <span>⭐</span> <strong>Top Result</strong><br>
                <a href="${top.link}" target="_blank">${top.title}</a>
                <p>${top.snippet}</p>
            </div>
        `;

        // OTHER RESULTS
        data.results.slice(1).forEach(item => {
            resultsDiv.innerHTML += `
                <div class="result-card fade-in">
                    <a href="${item.link}" target="_blank">${item.title}</a>
                    <p>${item.snippet}</p>
                </div>
            `;
        });

        // EXTRA SECTION
        resultsDiv.innerHTML += `<div class="extra-section">`;

        if(data.images && data.images.length>0){
            resultsDiv.innerHTML += `
                <div class="extra-card fade-in">
                    <span>🖼</span>
                    <div class="section-title">Images</div>
                    <a href="${data.images[0].link}" target="_blank">View</a>
                </div>
            `;
        }

        if(data.videos && data.videos.length>0){
            resultsDiv.innerHTML += `
                <div class="extra-card fade-in">
                    <span>🎥</span>
                    <div class="section-title">Videos</div>
                    <a href="${data.videos[0].link}" target="_blank">Watch</a>
                </div>
            `;
        }

        if(data.shopping && data.shopping.length>0){
            resultsDiv.innerHTML += `
                <div class="extra-card fade-in">
                    <span>🛒</span>
                    <div class="section-title">Shopping</div>
                    <a href="${data.shopping[0].link}" target="_blank">Shop</a>
                </div>
            `;
        }

        resultsDiv.innerHTML += `</div>`;

        // ⚡ TRIGGER ANIMATION
        document.querySelectorAll('.fade-in').forEach(el => {
            el.style.animation = 'none';
            void el.offsetWidth; // force reflow
            el.style.animation = 'fadeUp 0.6s forwards';
        });
        document.querySelectorAll('.extra-card span, .top-result span').forEach(el => {
            el.style.animation = 'none';
            void el.offsetWidth;
            el.style.animation = 'iconPop 0.8s forwards';
        });

    })
    .catch(err=>{
        console.error(err);
        resultsDiv.innerHTML="<p>❌ Failed to load results</p>";
    });
}

/* ================= ENTER KEY PRESS ================= */
document.getElementById("searchInput").addEventListener("keypress", function(e){
    if(e.key==="Enter") handleSearch();
});