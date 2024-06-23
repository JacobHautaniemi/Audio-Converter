from flask import Flask, request, render_template, redirect, url_for, send_file
from werkzeug.utils import secure_filename
import os
import PyPDF2
from gtts import gTTS
from pydub import AudioSegment

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            audio_file_path = convert_pdf_to_audio(file_path)

            # Delete the uploaded PDF file
            if os.path.exists(file_path):
                os.remove(file_path)

            return send_file(audio_file_path, as_attachment=True)
    return render_template('index.html')

def convert_pdf_to_audio(file_path):
    # Read the PDF file
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page_num in range(len(reader.pages)):
            text += reader.pages[page_num].extract_text()
    
    # Convert text to speech
    tts = gTTS(text=text, lang='en')
    audio_path = file_path.rsplit('.', 1)[0] + '.mp3'
    tts.save(audio_path)
    
    # Optionally, you can manipulate the audio using pydub if necessary
    # audio = AudioSegment.from_mp3(audio_path)
    # (Optional manipulations like volume adjustment)
    # audio.export(audio_path, format='mp3')
    
    return audio_path

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
