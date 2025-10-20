// Configuration
// For local development, defaults to localhost
// For production, set window.API_BASE_URL in your deployment
const API_BASE_URL = window.API_BASE_URL || 'http://localhost:5000/api';

// DOM Elements
const registrationForm = document.getElementById('registration-form');
const historyForm = document.getElementById('history-form');
const registrationMessage = document.getElementById('registration-message');
const historyMessage = document.getElementById('history-message');
const conversationContainer = document.getElementById('conversation-container');
const conversationList = document.getElementById('conversation-list');
const userNameSpan = document.getElementById('user-name');

// Utility Functions
function showMessage(element, message, type) {
    element.textContent = message;
    element.className = `message show ${type}`;
}

function hideMessage(element) {
    element.className = 'message';
}

function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function createMessageElement(message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message-item ${message.role}`;
    
    const roleName = message.role === 'user' ? 'You' : 'Support Bot';
    const emoji = message.role === 'user' ? '✉️' : '💝';
    
    messageDiv.innerHTML = `
        <div class="message-header">
            <span class="message-role">${emoji} ${roleName}</span>
            <span class="message-timestamp">${formatTimestamp(message.timestamp)}</span>
        </div>
        <div class="message-content">${escapeHtml(message.content)}</div>
    `;
    
    return messageDiv;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Registration Handler
registrationForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    hideMessage(registrationMessage);
    
    const formData = {
        email: document.getElementById('reg-email').value.trim(),
        name: document.getElementById('reg-name').value.trim(),
        occupation: document.getElementById('reg-occupation').value.trim(),
        interests: document.getElementById('reg-interests').value.trim(),
        hobbies: document.getElementById('reg-hobbies').value.trim(),
        personality: document.getElementById('reg-personality').value.trim()
    };
    
    // Disable submit button
    const submitBtn = registrationForm.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="loading"></span> Registering...';
    
    try {
        const response = await fetch(`${API_BASE_URL}/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            showMessage(registrationMessage, data.message, 'success');
            registrationForm.reset();
        } else {
            showMessage(registrationMessage, data.error || 'Registration failed', 'error');
        }
    } catch (error) {
        console.error('Registration error:', error);
        showMessage(registrationMessage, 'Failed to connect to server. Please try again.', 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
    }
});

// History Viewer Handler
historyForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    hideMessage(historyMessage);
    conversationContainer.classList.add('hidden');
    
    const email = document.getElementById('history-email').value.trim();
    
    // Disable submit button
    const submitBtn = historyForm.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="loading"></span> Loading...';
    
    try {
        // Fetch user info
        const userResponse = await fetch(`${API_BASE_URL}/user/${encodeURIComponent(email)}`);
        const userData = await userResponse.json();
        
        if (!userData.success) {
            showMessage(historyMessage, 'Email not found. Please register first.', 'error');
            return;
        }
        
        // Fetch conversation history
        const historyResponse = await fetch(`${API_BASE_URL}/history/${encodeURIComponent(email)}`);
        const historyData = await historyResponse.json();
        
        if (!historyData.success) {
            showMessage(historyMessage, 'Failed to load conversation history.', 'error');
            return;
        }
        
        // Display conversation
        userNameSpan.textContent = userData.user.name;
        conversationList.innerHTML = '';
        
        if (historyData.messages.length === 0) {
            conversationList.innerHTML = `
                <div class="empty-state">
                    <p>No conversation history yet.</p>
                    <p>Send an email to your support partner to start your conversation!</p>
                </div>
            `;
        } else {
            historyData.messages.forEach(message => {
                conversationList.appendChild(createMessageElement(message));
            });
            
            // Scroll to bottom
            conversationList.scrollTop = conversationList.scrollHeight;
        }
        
        conversationContainer.classList.remove('hidden');
        
        // Scroll to conversation
        conversationContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        
    } catch (error) {
        console.error('History fetch error:', error);
        showMessage(historyMessage, 'Failed to connect to server. Please try again.', 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
    }
});

