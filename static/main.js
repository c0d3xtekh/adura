const chatWindow = document.getElementById('chat-window');
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const typingIndicator = document.getElementById('typing-indicator');

function addMessage(sender, text, time = null) {
    const msgDiv = document.createElement('div');
    msgDiv.className = 'message ' + sender;
    const bubble = document.createElement('div');
    bubble.className = 'msg-bubble';
    bubble.innerHTML = text;
    msgDiv.appendChild(bubble);

    const timestamp = document.createElement('span');
    timestamp.className = 'timestamp';
    timestamp.innerText = time || new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    msgDiv.appendChild(timestamp);

    chatWindow.appendChild(msgDiv);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

function showTyping(show=true) {
    typingIndicator.style.display = show ? 'flex' : 'none';
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

chatForm.addEventListener('submit', function(e) {
    e.preventDefault();
    const text = userInput.value.trim();
    if (!text) return;
    addMessage('user', text);
    userInput.value = '';
    showTyping(true);

    fetch('/chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ message: text })
    })
    .then(res => res.json())
    .then(data => {
        showTyping(false);
        addMessage('bot', data.reply, data.timestamp);
    })
    .catch(() => {
        showTyping(false);
        addMessage('bot', "Oops, Adura couldn't reply 💔. Try again?", new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}));
    });
});

// Greeting on load
addMessage('bot', "Hey cutie! 💕 I'm Adura, your affectionate companion. How can I make your day golden?", new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}));
