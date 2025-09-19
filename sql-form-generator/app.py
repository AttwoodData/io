from flask import Flask, request, send_file, jsonify, render_template_string
import tempfile
import os
from form_parser import parse_docstring, generate_output_docstring

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit

# Example docstring - modify this for your specific use case
FORM_DEFINITION = """
@INSTANCE_ID NUMERIC(15)  False
@TYPE_CODE  CHAR(10) False
@VENDOR_NO  CHAR(11) True
@FIPS_CODE  NUMERIC(7) True
@NAME VARCHAR(30) False
@CODE NUMERIC(3) False
@CNTY_DIST_CODE CHAR(6)  True
@ELEM_DIST_IND CHAR(1)  True
@CAR_LAD_FLAG CHAR(1)  True
@EMAIL_ADDRESS  VARCHAR(70)  True
@BEGIN_DATE DATETIME2(7) False
@END_DATE   DATETIME2(7) False
@CREATED_USERID CHAR(10) False
@CREATED_DATE   DATETIME2(7) False
@LAST_MOD_USERID CHAR(10) True
@LAST_MOD_DATE  DATETIME2(7) True
@DUNS_NUMBER CHAR(9)  True
@NCES_IDVAR CHAR(30)  True
@CONGRESSIONAL_DISTRICT CHAR(2)  True
@CHARTER_TYPE_CODE  VARCHAR(10)  True
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
                    {% if field.get_max_length() and field.get_html_input_type() == 'text' %}maxlength="{{ field.get_max_length() }}"{% endif %}
                    {% if field.is_required %}required{% endif %}
                    data-type="{{ field.data_type }}"
                    data-required="{{ field.is_required }}"
                    data-display="{{ field.display_name }}"
                >
                <div class="error" id="error_{{ field.field_name }}"></div>
                {% if 'DATE' in field.data_type %}
                    <div class="hint">
                        {% if 'DATETIME' in field.data_type %}
                            Format: YYYY-MM-DD HH:MM (e.g., 2024-01-15 14:30)
                        {% else %}
                            Format: YYYY-MM-DD (e.g., 2024-01-15)
                        {% endif %}
                    </div>
                {% endif %}
            </div>
            {% endfor %}
            
            <button type="submit">Generate SQL Output</button>
        </form>
    </div>

    <script>
        document.getElementById('sqlForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Clear previous errors
            document.querySelectorAll('.error').forEach(error => {
                error.style.display = 'none';
            });
            
            let hasErrors = false;
            const formData = new FormData(this);
            
            // Validate each field
            document.querySelectorAll('input').forEach(input => {
                const value = input.value.trim();
                const isRequired = input.dataset.required === 'True';
                const dataType = input.dataset.type;
                const displayName = input.dataset.display;
                const errorDiv = document.getElementById('error_' + input.name);
                
                // Check if required field is empty
                if (isRequired && !value) {
                    errorDiv.textContent = displayName + ' is required';
                    errorDiv.style.display = 'block';
                    hasErrors = true;
                    return;
                }
                
                // Skip validation if field is empty and not required
                if (!value) return;
                
                // Validate data types
                if (dataType.includes('INT')) {
                    if (!/^\d+$/.test(value)) {
                        errorDiv.textContent = displayName + ' must be a whole number';
                        errorDiv.style.display = 'block';
                        hasErrors = true;
                    }
                } else if (dataType.includes('DECIMAL') || dataType.includes('FLOAT')) {
                    if (!/^\d*\.?\d+$/.test(value)) {
                        errorDiv.textContent = displayName + ' must be a number';
                        errorDiv.style.display = 'block';
                        hasErrors = true;
                    }
                }
                
                // Check string length
                const maxLengthMatch = dataType.match(/\((\d+)\)/);
                if (maxLengthMatch) {
                    const maxLength = parseInt(maxLengthMatch[1]);
                    if (value.length > maxLength) {
                        errorDiv.textContent = displayName + ' must be ' + maxLength + ' characters or less';
                        errorDiv.style.display = 'block';
                        hasErrors = true;
                    }
                }
            });
            
            // If no errors, submit the form
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