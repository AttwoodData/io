from flask import Flask, request, send_file, jsonify
import tempfile
import os
from parser import parse_pdf

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>PDF Text Extractor</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
            .upload-area { border: 2px dashed #ccc; padding: 40px; text-align: center; margin: 20px 0; }
            button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
            button:hover { background: #0056b3; }
        </style>
    </head>
    <body>
        <h1>PDF Text Extractor</h1>
        <div class="upload-area">
            <form method="POST" action="/extract" enctype="multipart/form-data">
                <p>Select a PDF file to extract text:</p>
                <input type="file" name="pdf_file" accept=".pdf" required>
                <br><br>
                <button type="submit">Extract Text</button>
            </form>
        </div>
        <p><small>Maximum file size: 16MB</small></p>
    </body>
    </html>
    '''

@app.route('/extract', methods=['POST'])
def extract_text():
    if 'pdf_file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['pdf_file']
    if file.filename == '' or not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Please upload a PDF file'}), 400
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf:
            file.save(temp_pdf.name)
            
            # Extract text using your parser
            extracted_text = parse_pdf(temp_pdf.name)
            
            # Create text file for download
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as temp_txt:
                temp_txt.write(extracted_text)
                temp_txt_path = temp_txt.name
            
            # Clean up PDF temp file
            os.unlink(temp_pdf.name)
            
            # Send text file as download
            original_name = file.filename.rsplit('.', 1)[0]
            return send_file(temp_txt_path, 
                           as_attachment=True, 
                           download_name=f"{original_name}_extracted.txt")
    
    except Exception as e:
        return jsonify({'error': f'Failed to extract text: {str(e)}'}), 500

@app.route('/health')
def health():
    return {'status': 'healthy'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)