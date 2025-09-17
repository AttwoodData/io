# PDF Text Extractor

A simple web service that extracts text from PDF files.

## Usage

1. Visit the web interface
2. Upload a PDF file
3. Download the extracted text file

## API Usage
```bash
curl -X POST -F "pdf_file=@document.pdf" \
  https://your-app-url.com/extract \
  --output extracted_text.txt