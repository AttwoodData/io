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
    
    // Get model selection from radio button
    const selectedRadio = document.querySelector('input[name="llm-model"]:checked');
    const modelPreference = selectedRadio ? selectedRadio.value : 'local-general';
    
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
    
    // Send to server with model preference
    fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
            message: message,
            model_preference: modelPreference  // Send selected model
        })
    })
    .then(response => response.json())
    .then(data => {
        showLoading(false);
        
        if (data.success) {
            appendMessage('assistant', data.assistant_message, data.timestamp);
            
            // Update model indicator with response info
            updateModelDisplay(data);
            
            // Sync radio button if auto-switched
            if (data.auto_switched) {
                syncRadioButton(data.model_used, true);
            }
            
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