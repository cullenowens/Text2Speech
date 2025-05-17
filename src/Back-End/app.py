from flask import Flask, request, jsonify
import os
from docx import Document

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_file():
    uploaded_file = request.files.get('file')
    if not uploaded_file:
        return jsonify({'error': 'No file provided'}), 400
    
    filename = uploaded_file.filename
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    uploaded_file.save(filepath)

    if filename.endswith('.txt'):
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
    elif filename.endswith('.docx'):
        doc = Document(filepath)
        content = "\n".join([para.text for para in doc.paragraphs])
    else:
        return jsonify({'error': 'Unsupported file type'}), 400
    return jsonify({'content': content})