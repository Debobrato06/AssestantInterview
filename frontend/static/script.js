const appStatus = document.getElementById('app-status');
const statusText = appStatus.querySelector('.status-text');
const toggleBtn = document.getElementById('toggle-btn');
const transcriptionBox = document.getElementById('transcription-box');
const answerChat = document.getElementById('answer-chat');
const typingIndicator = document.getElementById('typing-indicator');
const visualizer = document.getElementById('visualizer');
const historyList = document.getElementById('history-list');
const deviceSelect = document.getElementById('device-select');
const keywordPills = document.getElementById('keyword-pills');
const talkingPointsList = document.getElementById('talking-points');
const followUpBox = document.getElementById('follow-up-box');

let socket;
let isListening = false;

// Initialize WebSocket
function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    socket = new WebSocket(`${protocol}//${window.location.host}/ws`);

    socket.onopen = () => {
        appStatus.classList.add('active');
        statusText.innerText = 'ONLINE';
        initializeAppData();
    };

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleSocketMessage(data);
    };

    socket.onclose = () => {
        appStatus.classList.remove('active');
        statusText.innerText = 'OFFLINE';
        setTimeout(connectWebSocket, 3000);
    };
}

function handleSocketMessage(data) {
    switch (data.type) {
        case 'question':
            transcriptionBox.innerText = `"${data.content}"`;
            appendBubble(data.content, 'user-q');
            addToLog(data.content);
            break;
        case 'answer':
            typingIndicator.style.display = 'none';
            // Data.content is now a JSON object from GPT
            try {
                const responseObj = data.content;
                updateProPanels(responseObj);
                appendBubble(responseObj.main_answer, 'ai');
                if (responseObj.star_expansion) {
                    appendBubble(responseObj.star_expansion, 'ai star');
                }
            } catch (e) {
                console.error("Failed to parse GPT response", e);
                appendBubble(data.content, 'ai');
            }
            break;
        case 'status':
            if (data.content === 'Thinking...') {
                typingIndicator.style.display = 'flex';
                answerChat.scrollTop = answerChat.scrollHeight;
            }
            break;
    }
}

function updateProPanels(res) {
    // Keywords
    keywordPills.innerHTML = '';
    res.keywords.forEach(kw => {
        const span = document.createElement('span');
        span.className = 'pill';
        span.innerText = kw;
        keywordPills.appendChild(span);
    });

    // Talking Points
    talkingPointsList.innerHTML = '';
    res.talking_points.forEach(tp => {
        const li = document.createElement('li');
        li.innerText = tp;
        talkingPointsList.appendChild(li);
    });

    // Follow up
    followUpBox.innerText = res.interviewer_question || "Ready for next round.";
}

function appendBubble(text, type) {
    const p = document.createElement('div');
    p.className = `bubble ${type}`;
    p.innerText = text;

    // Insert before typing indicator
    answerChat.insertBefore(p, typingIndicator);
    answerChat.scrollTop = answerChat.scrollHeight;
}

async function initializeAppData() {
    try {
        const statusRes = await fetch('/status');
        const statusData = await statusRes.json();
        updateUI(statusData.is_listening);

        const devicesRes = await fetch('/devices');
        const devices = await devicesRes.json();

        deviceSelect.innerHTML = '<option value="">🎤 Audio Input</option>';
        devices.forEach(dev => {
            const opt = document.createElement('option');
            opt.value = dev.index;
            opt.innerText = dev.name;
            deviceSelect.appendChild(opt);
        });
    } catch (err) {
        console.error("Initialization failed", err);
    }
}

async function selectDevice() {
    const index = deviceSelect.value;
    if (index === "") return;
    await fetch('/select-device', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ index: parseInt(index) })
    });
}

async function toggleListening() {
    const response = await fetch('/toggle-listening', { method: 'POST' });
    const data = await response.json();
    updateUI(data.status === 'listening');
}

function updateUI(listening) {
    isListening = listening;
    if (listening) {
        toggleBtn.innerHTML = '<span class="icon">⏹️</span> DEACTIVATE COPILOT';
        toggleBtn.classList.add('active');
        visualizer.parentElement.parentElement.classList.add('active');
    } else {
        toggleBtn.innerHTML = '<span class="icon">⚡</span> ACTIVATE COPILOT';
        toggleBtn.classList.remove('active');
        visualizer.parentElement.parentElement.classList.remove('active');
    }
}

function addToLog(question) {
    const emptyLog = historyList.querySelector('.empty-log');
    if (emptyLog) emptyLog.remove();

    const div = document.createElement('div');
    div.className = 'history-item';
    div.innerHTML = `
        <span class="time">${new Date().toLocaleTimeString()}</span>
        <div class="q">${question}</div>
    `;
    historyList.prepend(div);
}

// Global actions
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        const bubbles = answerChat.querySelectorAll('.bubble');
        bubbles.forEach(b => b.remove());
    }
});

toggleBtn.addEventListener('click', toggleListening);
deviceSelect.addEventListener('change', selectDevice);

connectWebSocket();
