from flask import Flask, request, send_file, jsonify, render_template_string
import tempfile
import os
from form_parser import parse_docstring, generate_output_docstring

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit

# Test form definition using simplified three-class system
FORM_DEFINITION = """
@USER_ID INT True 'User ID'
@EMPLOYEE_EMAIL VARCHAR(100) True 'Email Address'
@SALARY MONEY False 'Annual Salary'
@BIRTH_DATE DATE False 'Date of Birth'
@START_TIME TIME False 'Start Time'
@LAST_LOGIN DATETIME False 'Last Login'
@IS_ACTIVE BIT True 'Active Status'
@SCORE DECIMAL(5,2) False 'Performance Score'
@NOTES VARCHAR(500) False 'Additional Notes'
"""

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>SQL Form Generator</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            max-width: 800px; 
            margin: 50px auto; 
            padding: 20px; 
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }
        h1 { 
            color: #333; 
            text-align: center;
            margin-bottom: 30px;
        }
        .field-group { 
            margin-bottom: 20px; 
        }
        label { 
            display: block; 
            margin-bottom: 5px; 
            font-weight: bold; 
            color: #555;
        }
        .required::after { 
            content: " *"; 
            color: red; 
        }
        input[type="text"], input[type="number"], input[type="date"], input[type="datetime-local"] { 
            width: 100%; 
            padding: 10px; 
            border: 2px solid #ddd; 
            border-radius: 5px; 
            box-sizing: border-box;
            font-size: 14px;
        }
        input:focus {
            border-color: #007bff;
            outline: none;
        }
        .error { 
            color: red; 
            font-size: 12px; 
            margin-top: 5px;
            display: none;
        }
        .hint {
            color: #666;
            font-size: 12px;
            margin-top: 5px;
            font-style: italic;
        }
        button { 
            background: #007bff; 
            color: white; 
            padding: 12px 30px; 
            border: none; 
            border-radius: 5px; 
            cursor: pointer; 
            font-size: 16px;
            width: 100%;
            margin-top: 20px;
        }
        button:hover { 
            background: #0056b3; 
        }
        button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        .success {
            color: green;
            text-align: center;
            margin: 20px 0;
        }
        .definition-box {
            background: #f8f9fa;
            border-left: 4px solid #007bff;
            padding: 15px;
            margin-bottom: 30px;
            font-family: monospace;
            white-space: pre-wrap;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>SQL Form Generator</h1>
        
        <div class="definition-box">
            <strong>Form Definition:</strong>
            {{ form_definition }}
        </div>

        <form id="sqlForm" method="POST" action="/generate">
            {% for field in fields %}
            <div class="field-group">
                <label for="{{ field.field_name }}" {% if field.is_required %}class="required"{% endif %}>
                    {{ field.display_name }}
                    {% if field.get_max_length() %}(max {{ field.get_max_length() }} characters){% endif %}
                </label>
                <input 
                    type="{{ field.get_html_input_type() }}" 
                    id="{{ field.field_name }}" 
                    name="{{ field.field_name }}"
                    {% for attr, value in field.get_html_attributes().items() %}
                        {{ attr }}="{{ value }}"
                    {% endfor %}
                    {% if field.is_required %}required{% endif %}
                    data-type="{{ field.data_type }}"
                    data-required="{{ field.is_required }}"
                    data-display="{{ field.display_name }}"
                >
                <div class="error" id="error_{{ field.field_name }}"></div>
                {% if field.data_type.upper() == 'DATETIME' %}
                    <div class="hint">
                        Formats: YYYY-MM-DD HH:MM:SS, YYYY-MM-DD HH:MM, or YYYY-MM-DD<br>
                        Examples: 2024-01-15 14:30:00, 2024-01-15 14:30, or 2024-01-15
                    </div>
                {% endif %}
            </div>
            {% endfor %}
            
            <button type="submit">Generate SQL Output</button>
        </form>
    </div>

    <script>
        // Real-time validation using HTML5 constraint validation
        document.addEventListener('DOMContentLoaded', function() {
            // Add custom validation for each field
            document.querySelectorAll('input').forEach(input => {
                const dataType = input.dataset.type.toUpperCase();
                
                // Custom validation for specific types
                input.addEventListener('input', function(e) {
                    const value = e.target.value;
                    const errorDiv = document.getElementById('error_' + input.name);
                    let errorMessage = '';
                    
                    // BIT validation - only 0 or 1
                    if (dataType.includes('BIT') && value && !['0', '1'].includes(value)) {
                        errorMessage = input.dataset.display + ' must be 0 or 1';
                    }
                    // TINYINT validation - 0 to 255
                    else if (dataType.includes('TINYINT') && value) {
                        const intVal = parseInt(value);
                        if (isNaN(intVal) || intVal < 0 || intVal > 255) {
                            errorMessage = input.dataset.display + ' must be between 0 and 255';
                        }
                    }
                    // SMALLINT validation - -32768 to 32767
                    else if (dataType.includes('SMALLINT') && value) {
                        const intVal = parseInt(value);
                        if (isNaN(intVal) || intVal < -32768 || intVal > 32767) {
                            errorMessage = input.dataset.display + ' must be between -32,768 and 32,767';
                        }
                    }
                    // MONEY validation - max 2 decimal places
                    else if (dataType.includes('MONEY') && value && value.includes('.')) {
                        const decimals = value.split('.')[1];
                        if (decimals && decimals.length > 2) {
                            errorMessage = input.dataset.display + ' can have at most 2 decimal places';
                        }
                    }
                    
                    // Show/hide error
                    if (errorMessage) {
                        errorDiv.textContent = errorMessage;
                        errorDiv.style.display = 'block';
                        e.target.setCustomValidity(errorMessage);
                    } else {
                        errorDiv.style.display = 'none';
                        e.target.setCustomValidity('');
                    }
                });
                
                // Prevent invalid keystrokes for integer types
                if (['BIT', 'TINYINT', 'SMALLINT', 'INT', 'INTEGER', 'BIGINT', 'NUMERIC'].some(t => dataType.includes(t))) {
                    input.addEventListener('keypress', function(e) {
                        // Allow: backspace, delete, tab, escape, enter, home, end, left, right
                        if ([8, 9, 27, 13, 46, 35, 36, 37, 39].indexOf(e.keyCode) !== -1 ||
                            // Allow: Ctrl+A, Ctrl+C, Ctrl+V, Ctrl+X
                            (e.keyCode === 65 && e.ctrlKey === true) ||
                            (e.keyCode === 67 && e.ctrlKey === true) ||
                            (e.keyCode === 86 && e.ctrlKey === true) ||
                            (e.keyCode === 88 && e.ctrlKey === true)) {
                            return;
                        }
                        // Ensure that it is a number and stop the keypress
                        if ((e.shiftKey || (e.keyCode < 48 || e.keyCode > 57)) && (e.keyCode < 96 || e.keyCode > 105)) {
                            e.preventDefault();
                        }
                        // Allow minus only for signed integers and only at start
                        if (e.keyCode === 45 && !dataType.includes('TINYINT') && !dataType.includes('BIT') && input.selectionStart === 0) {
                            return;
                        }
                    });
                }
            });
        });

        document.getElementById('sqlForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Clear previous errors
            document.querySelectorAll('.error').forEach(error => {
                error.style.display = 'none';
            });
            
            let hasErrors = false;
            const formData = new FormData(this);
            
            // Check HTML5 validation first
            if (!this.checkValidity()) {
                // Show validation errors
                document.querySelectorAll('input:invalid').forEach(input => {
                    const errorDiv = document.getElementById('error_' + input.name);
                    errorDiv.textContent = input.validationMessage || 'Invalid value';
                    errorDiv.style.display = 'block';
                    hasErrors = true;
                });
            }
            
            // Additional custom validation
            document.querySelectorAll('input').forEach(input => {
                const value = input.value.trim();
                const isRequired = input.dataset.required === 'True';
                const dataType = input.dataset.type.toUpperCase();
                const displayName = input.dataset.display;
                const errorDiv = document.getElementById('error_' + input.name);
                
                // Required field check
                if (isRequired && !value) {
                    errorDiv.textContent = displayName + ' is required';
                    errorDiv.style.display = 'block';
                    hasErrors = true;
                    return;
                }
                
                if (!value) return; // Skip validation for empty optional fields
                
                // Additional validation checks
                if (dataType.includes('EMAIL') && value) {
                    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                    if (!emailRegex.test(value)) {
                        errorDiv.textContent = displayName + ' must be a valid email address';
                        errorDiv.style.display = 'block';
                        hasErrors = true;
                    }
                }
            });
            
            // Submit if no errors
            if (!hasErrors) {
                fetch('/generate', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.blob())
                .then(blob => {
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'sql_output.txt';
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    document.body.removeChild(a);
                    
                    // Show success message
                    const successDiv = document.createElement('div');
                    successDiv.className = 'success';
                    successDiv.textContent = 'SQL output file downloaded successfully!';
                    this.parentNode.insertBefore(successDiv, this);
                    
                    setTimeout(() => successDiv.remove(), 3000);
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('An error occurred while generating the output.');
                });
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    fields = parse_docstring(FORM_DEFINITION)
    return render_template_string(HTML_TEMPLATE, fields=fields, form_definition=FORM_DEFINITION)

@app.route('/generate', methods=['POST'])
def generate_output():
    try:
        fields = parse_docstring(FORM_DEFINITION)
        form_data = {}
        errors = []
        
        # Collect and validate form data
        for field in fields:
            value = request.form.get(field.field_name, '').strip()
            form_data[field.field_name] = value
            
            # Server-side validation
            is_valid, error_message = field.validate_value(value)
            if not is_valid:
                errors.append(error_message)
        
        if errors:
            return jsonify({'errors': errors}), 400
        
        # Generate output docstring
        output = generate_output_docstring(fields, form_data)
        
        # Create temporary file for download
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as temp_file:
            temp_file.write(output)
            temp_file_path = temp_file.name
        
        return send_file(temp_file_path, 
                        as_attachment=True, 
                        download_name='sql_output.txt')
    
    except Exception as e:
        return jsonify({'error': f'Failed to generate output: {str(e)}'}), 500

@app.route('/health')
def health():
    return {'status': 'healthy'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)