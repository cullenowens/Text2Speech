from flask import Flask, request, jsonify, render_template, send_from_directory
import os
from docx import Document
import pyttsx3

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

app = Flask(__name__,
            template_folder=os.path.join(os.pardir, 'frontend', 'templates'),
            #static_folder=os.path.join(os.pardir, 'static'))
            static_folder=os.path.join(basedir, 'static'))
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
print("Resolved STATIC FOLDER:", app.static_folder)

#TTS Class

from gtts import gTTS

class TextToSpeech:
    def __init__(self, output_dir=os.path.join(os.pardir, 'src', 'static', 'audio'), filename='output.mp3'):
        self.output_dir = output_dir
        print(f"[DEBUG] Output directory: {self.output_dir}")
        self.filename = filename
        print(f"[DEBUG] Filename: {self.filename}")
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_audio(self, text, lang='en'):
        audio_path = os.path.join(self.output_dir, self.filename)
        tts = gTTS(text=text, lang=lang)
        print(f"[DEBUG] Saving audio to: {audio_path}")
        tts.save(audio_path)
        if not os.path.exists(audio_path):
            print(f"[ERROR] Audio file not created at {audio_path}")
        else:
            print(f"[DEBUG] Audio file created successfully at {audio_path}")
        # Ensure the audio file is saved correctly
        print(f"[DEBUG] Saving audio to: {os.path.abspath(audio_path)}")
        return os.path.join('audio', self.filename)

@app.route('/')
def home():
    return render_template('page.html')

@app.route('/uploads', methods=['POST'])
#fix where file is uploaded
def upload_file():
    uploaded_file = request.files.get('file')
    if not uploaded_file:
        return jsonify({'error': 'No file provided'}), 400

    filename = uploaded_file.filename
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    uploaded_file.save(filepath)
    print(f" [DEBUG] File saved to {filepath}")

    if filename.endswith('.txt'):
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
    elif filename.endswith('.docx'):
        doc = Document(filepath)
        content = "\n".join([para.text for para in doc.paragraphs])
    else:
        return jsonify({'error': 'Unsupported file type'}), 400

    tts = TextToSpeech()
    audio_path = tts.generate_audio(content)

    audio_url = os.path.join('audio', os.path.basename(audio_path))
    full_path = os.path.join(os.pardir, 'static', 'audio', 'output.mp3')
    print(f"[DEBUG] Full static file path: {os.path.abspath(full_path)}")
    print(f"[DEBUG] File exists? {os.path.exists(full_path)}")
    return render_template('page.html', content=content, audio_file=True, audio_path=audio_url)

if __name__ == '__main__':
    app.run(debug=True)
#runtime loop errors when audio is attempting to be generated
# app.py