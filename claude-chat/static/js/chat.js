// Chat JavaScript
// Claude Chat Application - Client-Side Logic

document.addEventListener('DOMContentLoaded', function() {
    console.log('Claude Chat initialized');
    initializeChat();
});

function initializeChat() {
    // Get DOM elements
    const chatForm = document.getElementById('chat-form');
    const messageInput = document.getElementById('message-input');
    const sendBtn = document.getElementById('send-btn');
    const newChatBtn = document.getElementById('new-chat-btn');
    const exportBtn = document.getElementById('export-btn');
    const messagesContainer = document.getElementById('messages-container');
    const charCount = document.getElementById('char-count');
    const loadingOverlay = document.getElementById('loading-overlay');
    
    // Check API connection status
    checkConnectionStatus();
    
    // Initialize character counter
    messageInput.addEventListener('input', function() {
        const currentLength = this.value.length;
        charCount.textContent = currentLength;
        
        // Change color as approaching limit
        if (currentLength > 3500) {
            charCount.style.color = '#e53e3e';
        } else if (currentLength > 3000) {
            charCount.style.color = '#dd6b20';
        } else {
            charCount.style.color = '#a0aec0';
        }
    });
    
    // Handle Enter key (Shift+Enter for new line)
    messageInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            chatForm.dispatchEvent(new Event('submit'));
        }
    });
    
    // Handle form submission
    if (chatForm) {
        chatForm.addEventListener('submit', handleMessageSubmit);
    }
    
    // Handle "Ask Another Question" button
    const askAnotherBtn = document.getElementById('ask-another');
    if (askAnotherBtn) {
        askAnotherBtn.addEventListener('click', resetForm);
    }
    
    // Handle new chat button
    if (newChatBtn) {
        newChatBtn.addEventListener('click', handleNewChat);
    }
    
    // Handle export button
    if (exportBtn) {
        exportBtn.addEventListener('click', handleExport);
    }
}

function checkConnectionStatus() {
    const statusDot = document.querySelector('.status-dot');
    const statusText = document.querySelector('.status-text');
    
    fetch('/health')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'healthy' && data.claude_api === 'connected') {
                statusDot.className = 'status-dot connected';
                statusText.textContent = 'Connected';
                console.log('Claude API: Connected');
            } else {
                statusDot.className = 'status-dot error';
                statusText.textContent = 'API Error';
                console.warn('Claude API: Not connected');
            }
        })
        .catch(error => {
            statusDot.className = 'status-dot error';
            statusText.textContent = 'Offline';
            console.error('Connection check failed:', error);
        });
}

function handleMessageSubmit(event) {
    event.preventDefault();
    
    const messageInput = document.getElementById('message-input');
    const message = messageInput.value.trim();
    
    // Validate message
    if (!message) {
        showError('Please enter a message');
        return;
    }
    
    if (message.length > 4000) {
        showError('Message too long. Please limit to 4000 characters.');
        return;
    }
    
    // Clear welcome message if it exists
    const welcomeMessage = document.querySelector('.welcome-message');
    if (welcomeMessage) {
        welcomeMessage.remove();
    }
    
    // Display user message immediately
    appendMessage('user', message);
    
    // Clear input
    messageInput.value = '';
    document.getElementById('char-count').textContent = '0';
    
    // Show loading state
    showLoading(true);
    
    // Send to server
    fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: message })
    })
    .then(response => response.json())
    .then(data => {
        showLoading(false);
        
        if (data.success) {
            appendMessage('assistant', data.assistant_message, data.timestamp);
            messageInput.focus();
        } else {
            showError(data.error || 'Failed to get response');
        }
    })
    .catch(error => {
        showLoading(false);
        console.error('Error:', error);
        showError('Unable to connect to server. Please try again.');
    });
}

function appendMessage(role, content, timestamp) {
    const messagesContainer = document.getElementById('messages-container');
    
    // Create message element
    const messageDiv = document.createElement('div');
    messageDiv.className = `message message-${role}`;
    
    // Format timestamp
    const timeStr = timestamp || new Date().toLocaleString('en-US', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    
    // Build message HTML
    messageDiv.innerHTML = `
        <div class="message-header">
            <span class="message-role">${role === 'user' ? 'You' : 'Claude'}</span>
            <span class="message-timestamp">${timeStr}</span>
        </div>
        <div class="message-content">${escapeHtml(content)}</div>
    `;
    
    // Append and scroll
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function handleNewChat() {
    if (!confirm('Start a new conversation? Current chat will be cleared.')) {
        return;
    }
    
    showLoading(true);
    
    fetch('/new-chat', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        showLoading(false);
        
        if (data.success) {
            // Clear messages
            const messagesContainer = document.getElementById('messages-container');
            messagesContainer.innerHTML = `
                <div class="welcome-message">
                    <div class="welcome-icon">
                        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                        </svg>
                    </div>
                    <h2>Start a Conversation with Claude</h2>
                    <p>Ask me anything! I'll maintain context throughout our conversation.</p>
                </div>
            `;
            
            // Clear and focus input
            const messageInput = document.getElementById('message-input');
            messageInput.value = '';
            document.getElementById('char-count').textContent = '0';
            messageInput.focus();
            
            console.log('New chat started');
        } else {
            showError(data.error || 'Failed to start new chat');
        }
    })
    .catch(error => {
        showLoading(false);
        console.error('Error:', error);
        showError('Unable to start new chat. Please try again.');
    });
}

function handleExport() {
    // Check if there are messages to export
    const messages = document.querySelectorAll('.message');
    if (messages.length === 0) {
        showError('No conversation to export');
        return;
    }
    
    showLoading(true);
    
    // Download the export file
    window.location.href = '/export';
    
    setTimeout(() => {
        showLoading(false);
    }, 1000);
}

function showLoading(show) {
    const loadingOverlay = document.getElementById('loading-overlay');
    const sendBtn = document.getElementById('send-btn');
    
    if (show) {
        loadingOverlay.style.display = 'flex';
        sendBtn.disabled = true;
    } else {
        loadingOverlay.style.display = 'none';
        sendBtn.disabled = false;
    }
}

function showError(message) {
    // Create error notification
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-notification';
    errorDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #fed7d7;
        color: #c53030;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #e53e3e;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 10000;
        animation: slideIn 0.3s ease;
        max-width: 400px;
    `;
    
    errorDiv.innerHTML = `
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="8" x2="12" y2="12"></line>
                <line x1="12" y1="16" x2="12.01" y2="16"></line>
            </svg>
            <span>${escapeHtml(message)}</span>
        </div>
    `;
    
    document.body.appendChild(errorDiv);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        errorDiv.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            errorDiv.remove();
        }, 300);
    }, 5000);
    
    console.error('Error displayed:', message);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function resetForm() {
    const questionInput = document.getElementById('question');
    const charCount = document.getElementById('char-count');
    
    // Reset form
    if (questionInput) {
        questionInput.value = '';
        charCount.textContent = '0';
        charCount.style.color = '#a0aec0';
    }
    
    // Hide sections
    const responseSection = document.getElementById('response-section');
    const errorSection = document.getElementById('error-section');
    
    if (responseSection) responseSection.style.display = 'none';
    if (errorSection) errorSection.style.display = 'none';
    
    // Focus on input
    if (questionInput) {
        questionInput.focus();
    }
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
    
    console.log('Form reset');
}

// Add CSS animation for error notification
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Handle any uncaught errors
window.addEventListener('error', function(event) {
    console.error('JavaScript error:', event.error);
});