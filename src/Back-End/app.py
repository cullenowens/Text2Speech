from flask import Flask, request, jsonify, render_template, send_from_directory
import os
from docx import Document
import pyttsx3

app = Flask(__name__,
            template_folder=os.path.join(os.pardir, 'frontend', 'templates'),
            static_folder=os.path.join(os.pardir, 'static'))
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

#TTS Class
class TextToSpeech:
    def __init__(self, output_dir=os.path.join(os.pardir, 'static', 'audio'), filename='output.mp3'):
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
        self.engine = pyttsx3.init()  # Reinitialize to reset properties
        audio_path = os.path.join(self.output_dir, self.filename)
        print(f"[DEBUG] Saving audio to: {audio_path}")
        self.engine.save_to_file(text, audio_path)
        self.engine.runAndWait()
        if not os.path.exists(audio_path):
            print("[ERROR] Audio file was not created.")
        return audio_path

@app.route('/')
def home():
    return render_template('page.html')

@app.route('/uploads', methods=['POST'])
def upload_file():
    uploaded_file = request.files.get('file')
    if not uploaded_file:
        return jsonify({'error': 'No file provided'}), 400
    
    voice = request.form.get('voice', 'female').lower()
    rate = int(request.form.get('rate', 150))
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
    tts.set_voice(voice)
    tts.set_rate(rate)
    print(f" [DEBUG] Generating audio with voice: {voice}, rate: {rate}")
    audio_path = tts.generate_audio(content)

    audio_url = os.path.join('audio', os.path.basename(audio_path))
    print(f" [DEBUG] Audio generated at {audio_url}")
    return render_template('page.html', content=content, audio_file=True, audio_path=audio_url)

if __name__ == '__main__':
    app.run(debug=True)
#runtime loop errors when audio is attempting to be generated
# app.py