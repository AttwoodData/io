// RAG Agent Factory - Main JavaScript
// Following project principle: simplicity over complexity

document.addEventListener('DOMContentLoaded', function() {
    console.log('RAG Agent Factory - Phase 1 loaded');
    
    // Initialize the application
    initializeApp();
});

function initializeApp() {
    // Get DOM elements
    const questionForm = document.getElementById('question-form');
    const questionInput = document.getElementById('question');
    const submitBtn = document.getElementById('submit-btn');
    const responseSection = document.getElementById('response-section');
    const errorSection = document.getElementById('error-section');
    const statusIndicator = document.getElementById('status-indicator');
    
    // Initialize character counter
    initializeCharacterCounter();
    
    // Check Ollama connection status
    checkOllamaStatus();
    
    // Handle form submission
    if (questionForm) {
        questionForm.addEventListener('submit', handleQuestionSubmit);
    }
    
    // Handle "Ask Another Question" button
    const askAnotherBtn = document.getElementById('ask-another');
    if (askAnotherBtn) {
        askAnotherBtn.addEventListener('click', resetForm);
    }
    
    // Handle "Try Again" button
    const tryAgainBtn = document.getElementById('try-again');
    if (tryAgainBtn) {
        tryAgainBtn.addEventListener('click', resetForm);
    }
}

function initializeCharacterCounter() {
    const questionInput = document.getElementById('question');
    const charCount = document.getElementById('char-count');
    
    if (questionInput && charCount) {
        questionInput.addEventListener('input', function() {
            const currentLength = this.value.length;
            charCount.textContent = currentLength;
            
            // Change color as approaching limit
            if (currentLength > 800) {
                charCount.style.color = '#e53e3e';
            } else if (currentLength > 600) {
                charCount.style.color = '#dd6b20';
            } else {
                charCount.style.color = '#a0aec0';
            }
        });
    }
}

function checkOllamaStatus() {
    const statusIndicator = document.getElementById('status-indicator');
    const statusDot = statusIndicator.querySelector('.status-dot');
    const statusText = statusIndicator.querySelector('.status-text');
    
    // Check health endpoint
    fetch('/health')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'healthy' && data.ollama_connected) {
                statusDot.className = 'status-dot connected';
                statusText.textContent = 'Ollama connected';
                console.log('Ollama connection: OK');
            } else {
                statusDot.className = 'status-dot error';
                statusText.textContent = 'Ollama connection failed';
                console.warn('Ollama connection: Failed');
            }
        })
        .catch(error => {
            statusDot.className = 'status-dot error';
            statusText.textContent = 'System unavailable';
            console.error('Health check failed:', error);
        });
}

function handleQuestionSubmit(event) {
    event.preventDefault();
    
    const questionInput = document.getElementById('question');
    const question = questionInput.value.trim();
    
    // Basic validation
    if (!question) {
        showError('Please enter a question');
        return;
    }
    
    if (question.length < 3) {
        showError('Question must be at least 3 characters long');
        return;
    }
    
    if (question.length > 1000) {
        showError('Question must be less than 1000 characters');
        return;
    }
    
    // Show loading state
    setLoadingState(true);
    hideError();
    hideResponse();
    
    // Send question to server
    const formData = new FormData();
    formData.append('question', question);
    
    fetch('/ask', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        setLoadingState(false);
        
        if (data.success) {
            showResponse(data);
        } else {
            showError(data.error || 'An error occurred while processing your question');
        }
    })
    .catch(error => {
        setLoadingState(false);
        console.error('Error:', error);
        showError('Unable to connect to the server. Please try again.');
    });
}

function setLoadingState(isLoading) {
    const submitBtn = document.getElementById('submit-btn');
    const buttonText = submitBtn.querySelector('.button-text');
    const loadingSpinner = submitBtn.querySelector('.loading-spinner');
    
    if (isLoading) {
        submitBtn.disabled = true;
        buttonText.style.display = 'none';
        loadingSpinner.style.display = 'inline-block';
    } else {
        submitBtn.disabled = false;
        buttonText.style.display = 'inline-block';
        loadingSpinner.style.display = 'none';
    }
}

function showResponse(data) {
    const responseSection = document.getElementById('response-section');
    const responseContent = document.getElementById('response-content');
    const responseTimestamp = document.getElementById('response-timestamp');
    
    // Update content
    responseContent.textContent = data.answer;
    responseTimestamp.textContent = `Response generated at ${data.timestamp}`;
    
    // Show response section
    responseSection.style.display = 'block';
    
    // Scroll to response
    responseSection.scrollIntoView({ behavior: 'smooth' });
    
    console.log('Response displayed successfully');
}

function showError(message) {
    const errorSection = document.getElementById('error-section');
    const errorMessage = document.getElementById('error-message');
    
    errorMessage.textContent = message;
    errorSection.style.display = 'block';
    
    // Scroll to error
    errorSection.scrollIntoView({ behavior: 'smooth' });
    
    console.error('Error displayed:', message);
}

function hideResponse() {
    const responseSection = document.getElementById('response-section');
    responseSection.style.display = 'none';
}

function hideError() {
    const errorSection = document.getElementById('error-section');
    errorSection.style.display = 'none';
}

function resetForm() {
    const questionInput = document.getElementById('question');
    const charCount = document.getElementById('char-count');
    
    // Reset form
    questionInput.value = '';
    charCount.textContent = '0';
    charCount.style.color = '#a0aec0';
    
    // Hide sections
    hideResponse();
    hideError();
    
    // Focus on input
    questionInput.focus();
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
    
    console.log('Form reset');
}

// Utility function for debugging
function logInteraction(action, data = {}) {
    console.log(`[RAG Factory] ${action}:`, data);
}

// Handle any uncaught errors
window.addEventListener('error', function(event) {
    console.error('JavaScript error:', event.error);
    // Could send error reports to server in production
});
