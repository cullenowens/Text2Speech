from flask import Flask, request, jsonify, render_template, send_from_directory
import os
from docx import Document
import pyttsx3

app = Flask(__name__,
            template_folder=os.path.join(os.pardir, 'templates'),
            static_folder=os.path.join(os.pardir, 'static'))
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

#TTS Class
class TextToSpeech:
    def __init__(self, output_dir='frontend/static/audio', filename='output.mp3'):
        self.engine = pyttsx3.init()
        self.output_dir = output_dir
        self.filename = filename
        os.makedirs(self.output_dir, exist_ok=True)
    
    def set_voice(self, gender='male'):
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if gender in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break
    
    def set_rate(self, rate=150):
        self.engine.setProperty('rate', rate)
    
    def generate_audio(self, text):
        audio_path = os.path.join(self.output_dir, self.filename)
        self.engine.save_to_file(text, audio_path)
        self.engine.runAndWait()
        return audio_path

@app.route('/')
def home():
    return render_template('page.html')

@app.route('/uploads', methods=['POST'])
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

    return render_template('page.html', content=content, filename=filename)

@app.route('/generate_audio', methods=['POST'])
def generate_audio():
    text = request.form.get('text')
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    engine = pyttsx3.init()
    audio_filename = 'output.mp3'
    AUDIO_FOLDER = 'static/audio'
    audio_path = os.path.join(AUDIO_FOLDER, 'output.mp3')
    engine.save_to_file(text, audio_path)
    engine.runAndWait()

    return render_template('page.html', audio_path='audio/output.mp3', text=text)

if __name__ == '__main__':
    app.run(debug=True)
# app.py