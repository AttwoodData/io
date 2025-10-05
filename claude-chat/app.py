"""
Claude Chat Application - Secure API Integration with Manual Configuration
Simple Flask app for conversational interface with Claude API
Now supports manual configuration commands for optimal performance
"""

from flask import Flask, request, render_template, jsonify, session, send_file
from anthropic import Anthropic
import os
import logging
from datetime import datetime, timedelta
from functools import wraps
import tempfile
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

# Initialize Flask with secret key for sessions
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))
app.config['SESSION_COOKIE_SECURE'] = True  # HTTPS only
app.config['SESSION_COOKIE_HTTPONLY'] = True  # No JavaScript access
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/chat_app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Anthropic client
try:
    client = Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))
    logger.info("Claude API client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Claude API client: {e}")
    client = None

# Global default settings for Claude
DEFAULT_SETTINGS = {
    'model': 'claude-sonnet-4-5-20250929',  # Latest Sonnet 4.5
    'max_tokens': 3072,
    'temperature': 0.9,
    'system_prompt': 'You are a helpful, friendly AI assistant.'
}

# Configuration presets for different use cases
CONFIGURATION_PRESETS = {
    'creative_writing': {
        'model': 'claude-sonnet-4-5-20250929',
        'max_tokens': 4096,
        'temperature': 1.0,
        'system_prompt': 'You are a creative writing assistant. Help users craft engaging stories, poetry, and creative content with vivid descriptions and imaginative ideas.'
    },
    'coding': {
        'model': 'claude-sonnet-4-5-20250929',
        'max_tokens': 4096,
        'temperature': 0.3,
        'system_prompt': 'You are a programming expert. Provide clear, well-documented code with explanations. Focus on best practices, security, and maintainability.'
    },
    'analysis': {
        'model': 'claude-sonnet-4-5-20250929',
        'max_tokens': 4096,
        'temperature': 0.5,
        'system_prompt': 'You are an analytical assistant. Provide thorough, objective analysis with clear reasoning and evidence-based conclusions.'
    },
    'fast_responses': {
        'model': 'claude-haiku-3-5-20241022',
        'max_tokens': 2048,
        'temperature': 0.7,
        'system_prompt': 'You are a helpful assistant providing quick, concise responses.'
    },
    'detailed_explanations': {
        'model': 'claude-opus-4-20250514',
        'max_tokens': 4096,
        'temperature': 0.7,
        'system_prompt': 'You are a patient teacher who provides detailed, comprehensive explanations with examples.'
    },
    'casual_chat': {
        'model': 'claude-sonnet-4-5-20250929',
        'max_tokens': 2048,
        'temperature': 0.9,
        'system_prompt': 'You are a friendly conversational partner. Keep responses natural and engaging.'
    }
}

# Simple rate limiting
from collections import defaultdict
import time

request_counts = defaultdict(list)
RATE_LIMIT = 10  # requests
RATE_WINDOW = 60  # seconds

def rate_limit(f):
    """Simple rate limiting decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_id = request.remote_addr
        now = time.time()
        request_counts[client_id] = [
            req_time for req_time in request_counts[client_id]
            if now - req_time < RATE_WINDOW
        ]
        
        if len(request_counts[client_id]) >= RATE_LIMIT:
            logger.warning(f"Rate limit exceeded for {client_id}")
            return jsonify({
                'error': 'Rate limit exceeded. Please wait a moment.',
                'success': False
            }), 429
        
        request_counts[client_id].append(now)
        return f(*args, **kwargs)
    return decorated_function


def get_current_settings(session):
    """Get current Claude settings from session or defaults"""
    if 'claude_settings' not in session:
        session['claude_settings'] = DEFAULT_SETTINGS.copy()
        session.modified = True
    return session['claude_settings']


def is_configuration_request(message):
    """
    Detect if user is asking for configuration advice
    Returns: (is_config_request, config_type)
    """
    message_lower = message.lower()
    
    # Configuration command patterns
    config_patterns = [
        (r'\bconfigure\s+(yourself|settings|claude)\b', 'general'),
        (r'\bwhat\s+settings\s+(should|would|do)\b', 'advice'),
        (r'\bhow\s+should\s+(you|claude)\s+be\s+configured\b', 'advice'),
        (r'\boptimize\s+(yourself|settings)\s+for\b', 'optimize'),
        (r'\bset\s+up\s+for\b', 'optimize'),
        (r'\bbest\s+settings\s+for\b', 'advice'),
    ]
    
    for pattern, config_type in config_patterns:
        if re.search(pattern, message_lower):
            return True, config_type
    
    # Check for preset keywords
    for preset_name in CONFIGURATION_PRESETS.keys():
        if preset_name.replace('_', ' ') in message_lower:
            return True, preset_name
    
    return False, None


def is_settings_command(message):
    """Check if user wants to view current settings"""
    message_lower = message.lower().strip()
    return message_lower in [
        'show settings',
        'current settings',
        'what are your settings',
        'display settings',
        'settings'
    ]


def format_settings_display(settings):
    """Format settings for display to user"""
    return f"""
**Current Configuration:**
- **Model:** {settings['model']}
- **Max Tokens:** {settings['max_tokens']}
- **Temperature:** {settings['temperature']} (0=focused, 1=creative)
- **System Prompt:** {settings['system_prompt']}

**Available Presets:**
Type "configure for [preset]" to use:
- **creative_writing** - High creativity for stories and content
- **coding** - Precise, well-documented code
- **analysis** - Thorough, objective analysis
- **fast_responses** - Quick, concise answers (uses Haiku)
- **detailed_explanations** - Comprehensive teaching (uses Opus)
- **casual_chat** - Natural, friendly conversation

**Manual Commands:**
- "show settings" - Display current configuration
- "reset settings" - Return to defaults
- "configure for [task]" - Ask for recommendations
"""


def generate_configuration_advice(message, current_settings):
    """
    Use Claude to generate configuration advice based on user's needs
    This uses a meta-call to Claude to get recommendations
    """
    try:
        # Make a special call to Claude asking for configuration advice
        advice_prompt = f"""The user said: "{message}"

Based on this request, recommend optimal Claude configuration settings. Consider:
- Which model is best (claude-haiku-3-5-20241022 for speed, claude-sonnet-4-5-20250929 for balance, claude-opus-4-20250514 for quality)
- Max tokens (1024-4096)
- Temperature (0.0-1.0, where 0 is focused/deterministic and 1 is creative/diverse)
- System prompt to set the right personality/expertise

Respond in this exact format:
MODEL: [model name]
MAX_TOKENS: [number]
TEMPERATURE: [number]
SYSTEM_PROMPT: [prompt text]
EXPLANATION: [brief explanation of why these settings]"""

        advice_response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1024,
            temperature=0.3,
            messages=[{"role": "user", "content": advice_prompt}]
        )
        
        return advice_response.content[0].text
        
    except Exception as e:
        logger.error(f"Error generating configuration advice: {e}")
        return None


def parse_configuration_advice(advice_text):
    """Parse Claude's configuration advice into settings dict"""
    try:
        settings = {}
        
        # Extract model
        model_match = re.search(r'MODEL:\s*(.+?)(?:\n|$)', advice_text)
        if model_match:
            settings['model'] = model_match.group(1).strip()
        
        # Extract max_tokens
        tokens_match = re.search(r'MAX_TOKENS:\s*(\d+)', advice_text)
        if tokens_match:
            settings['max_tokens'] = int(tokens_match.group(1))
        
        # Extract temperature
        temp_match = re.search(r'TEMPERATURE:\s*([\d.]+)', advice_text)
        if temp_match:
            settings['temperature'] = float(temp_match.group(1))
        
        # Extract system prompt
        prompt_match = re.search(r'SYSTEM_PROMPT:\s*(.+?)(?=\nEXPLANATION:|$)', advice_text, re.DOTALL)
        if prompt_match:
            settings['system_prompt'] = prompt_match.group(1).strip()
        
        return settings
    except Exception as e:
        logger.error(f"Error parsing configuration advice: {e}")
        return None


@app.route('/')
def index():
    """Main chat interface"""
    if 'conversation_history' not in session:
        session['conversation_history'] = []
        session['claude_settings'] = DEFAULT_SETTINGS.copy()
        session.modified = True
    
    logger.info(f"User accessed main page from {request.remote_addr}")
    return render_template('index.html')


@app.route('/chat', methods=['POST'])
@rate_limit
def chat():
    """
    Handle chat messages and get Claude responses
    Supports configuration commands
    """
    if not client:
        return jsonify({
            'error': 'Claude API client not initialized. Check server configuration.',
            'success': False
        }), 500
    
    try:
        user_message = request.json.get('message', '').strip()
        
        if not user_message:
            return jsonify({
                'error': 'Message cannot be empty',
                'success': False
            }), 400
        
        if len(user_message) > 4000:
            return jsonify({
                'error': 'Message too long. Please limit to 4000 characters.',
                'success': False
            }), 400
        
        # Get current settings
        current_settings = get_current_settings(session)
        
        # Check for settings display command
        if is_settings_command(user_message):
            settings_display = format_settings_display(current_settings)
            return jsonify({
                'user_message': user_message,
                'assistant_message': settings_display,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'success': True,
                'is_system_message': True
            })
        
        # Check for reset command
        if user_message.lower().strip() in ['reset settings', 'default settings']:
            session['claude_settings'] = DEFAULT_SETTINGS.copy()
            session.modified = True
            return jsonify({
                'user_message': user_message,
                'assistant_message': '✅ Settings reset to defaults.\n\n' + format_settings_display(DEFAULT_SETTINGS),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'success': True,
                'is_system_message': True
            })
        
        # Check for preset configuration
        for preset_name, preset_settings in CONFIGURATION_PRESETS.items():
            if f'configure for {preset_name.replace("_", " ")}' in user_message.lower():
                session['claude_settings'] = preset_settings.copy()
                session.modified = True
                return jsonify({
                    'user_message': user_message,
                    'assistant_message': f'✅ Configured for **{preset_name.replace("_", " ").title()}**\n\n' + format_settings_display(preset_settings),
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'success': True,
                    'is_system_message': True
                })
        
        # Check if this is a configuration request
        is_config, config_type = is_configuration_request(user_message)
        
        if is_config:
            # Generate configuration advice
            advice = generate_configuration_advice(user_message, current_settings)
            
            if advice:
                # Try to parse the advice into settings
                suggested_settings = parse_configuration_advice(advice)
                
                response_text = f"Based on your request, here are my recommendations:\n\n{advice}\n\n"
                
                if suggested_settings:
                    response_text += "\n**To apply these settings, type:** `apply suggested settings`"
                    # Store suggested settings temporarily
                    session['suggested_settings'] = suggested_settings
                    session.modified = True
                
                response_text += "\n\nOr choose a preset by typing `configure for [preset name]`"
                
                return jsonify({
                    'user_message': user_message,
                    'assistant_message': response_text,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'success': True,
                    'is_system_message': True
                })
        
        # Check for apply suggested settings command
        if user_message.lower().strip() == 'apply suggested settings':
            if 'suggested_settings' in session:
                session['claude_settings'] = session['suggested_settings'].copy()
                session.modified = True
                return jsonify({
                    'user_message': user_message,
                    'assistant_message': '✅ Suggested settings applied!\n\n' + format_settings_display(session['claude_settings']),
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'success': True,
                    'is_system_message': True
                })
            else:
                return jsonify({
                    'user_message': user_message,
                    'assistant_message': 'No suggested settings found. Ask me for configuration advice first!',
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'success': True,
                    'is_system_message': True
                })
        
        # Normal chat processing
        conversation_history = session.get('conversation_history', [])
        
        # Build messages for Claude API
        messages = []
        for entry in conversation_history:
            messages.append({"role": "user", "content": entry['user']})
            messages.append({"role": "assistant", "content": entry['assistant']})
        
        messages.append({"role": "user", "content": user_message})
        
        logger.info(f"Processing message from {request.remote_addr}: {user_message[:50]}...")
        logger.info(f"Using settings: {current_settings['model']}, temp={current_settings['temperature']}")
        
        # Call Claude API with current settings
        response = client.messages.create(
            model=current_settings['model'],
            max_tokens=current_settings['max_tokens'],
            temperature=current_settings['temperature'],
            system=current_settings['system_prompt'],
            messages=messages
        )
        
        assistant_message = response.content[0].text
        
        # Update conversation history
        conversation_history.append({
            'user': user_message,
            'assistant': assistant_message,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
        session['conversation_history'] = conversation_history
        session.modified = True
        
        logger.info(f"Response generated successfully for {request.remote_addr}")
        
        return jsonify({
            'user_message': user_message,
            'assistant_message': assistant_message,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'success': True
        })
        
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}")
        return jsonify({
            'error': 'Failed to process message. Please try again.',
            'success': False
        }), 500


@app.route('/new-chat', methods=['POST'])
def new_chat():
    """Clear conversation history and start fresh"""
    try:
        session['conversation_history'] = []
        # Keep settings but clear conversation
        session.modified = True
        
        logger.info(f"Conversation reset for {request.remote_addr}")
        
        return jsonify({
            'message': 'Conversation cleared (settings preserved)',
            'success': True
        })
        
    except Exception as e:
        logger.error(f"Error clearing conversation: {str(e)}")
        return jsonify({
            'error': 'Failed to clear conversation',
            'success': False
        }), 500


@app.route('/export', methods=['GET'])
def export_conversation():
    """Export conversation history as text file"""
    try:
        conversation_history = session.get('conversation_history', [])
        
        if not conversation_history:
            return jsonify({
                'error': 'No conversation to export',
                'success': False
            }), 400
        
        # Create formatted text content
        lines = []
        lines.append("=" * 80)
        lines.append("CLAUDE CONVERSATION EXPORT")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 80)
        
        # Add current settings
        current_settings = get_current_settings(session)
        lines.append("\nCONFIGURATION:")
        lines.append(f"Model: {current_settings['model']}")
        lines.append(f"Temperature: {current_settings['temperature']}")
        lines.append(f"Max Tokens: {current_settings['max_tokens']}")
        lines.append(f"System Prompt: {current_settings['system_prompt']}")
        lines.append("\n" + "=" * 80)
        lines.append("")
        
        for i, entry in enumerate(conversation_history, 1):
            lines.append(f"--- Exchange {i} ({entry['timestamp']}) ---")
            lines.append("")
            lines.append(f"USER:")
            lines.append(entry['user'])
            lines.append("")
            lines.append(f"CLAUDE:")
            lines.append(entry['assistant'])
            lines.append("")
            lines.append("-" * 80)
            lines.append("")
        
        content = "\n".join(lines)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as tmp_file:
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        logger.info(f"Conversation exported for {request.remote_addr}")
        
        return send_file(
            tmp_path,
            as_attachment=True,
            download_name=f'claude_conversation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt',
            mimetype='text/plain'
        )
        
    except Exception as e:
        logger.error(f"Error exporting conversation: {str(e)}")
        return jsonify({
            'error': 'Failed to export conversation',
            'success': False
        }), 500


@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        if client:
            # Make a minimal test call
            test_response = client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=10,
                messages=[{"role": "user", "content": "Hi"}]
            )
            api_status = "connected"
        else:
            api_status = "not_initialized"
        
        return jsonify({
            'status': 'healthy',
            'claude_api': api_status,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


if __name__ == '__main__':
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    
    # Verify API key is set
    if not os.environ.get('ANTHROPIC_API_KEY'):
        logger.error("ANTHROPIC_API_KEY not set in environment!")
        print("ERROR: ANTHROPIC_API_KEY not found in environment variables")
        print("Please create a .env file with your API key")
        exit(1)
    
    logger.info("Starting Claude Chat Application with Manual Configuration")
    
    # For production, use gunicorn
    app.run(host='0.0.0.0', port=5005, debug=False)