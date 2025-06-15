from flask import Flask, request, jsonify, render_template, send_from_directory
import os
import time
from utils.audio_processor import AudioProcessor
import pdfplumber
from docx import Document

app = Flask(__name__, template_folder="templates", static_folder="static")

UPLOAD_FOLDER = "audio/uploads"
RESPONSE_FOLDER = "audio/responses"

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESPONSE_FOLDER, exist_ok=True)

processor = AudioProcessor()  # Initialize audio processor
resume_text = None
jobdesc = None

# ✅ FIXED: This correctly serves files with GET method
@app.route('/audio/uploads/<path:filename>', methods=['GET'])
def uploaded_audio(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/audio/responses/<path:filename>', methods=['GET'])
def response_audio(filename):
    return send_from_directory(RESPONSE_FOLDER, filename)

# 🔹 Upload audio route (Handles saving and bot response generation)
@app.route("/upload_audio", methods=["POST"])
def upload_audio():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400


    audio_file = request.files["audio"]
    timestamp = int(time.time())  # Unique filename with timestamp
    filename = f"recording_{timestamp}.wav"
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    # Save user audio
    audio_file.save(file_path)

    # Generate bot response audio
    _, response_audio = processor.update_chat(file_path)
    response_path = os.path.join(RESPONSE_FOLDER, os.path.basename(filename).split('.')[0]+'_resp.mp3')
    response_audio.export(response_path, format="mp3")

    return jsonify({
        "message": "Audio received",
        "audio_url": f"/audio/uploads/{filename}",  # 🔹 Corrected static path
        "response_audio_url": f"/audio/responses/{os.path.basename(response_path)}",
        "timestamp": timestamp
    })

#------------------------- RESUME --------------------------
def extract_text_from_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text.strip()

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs]).strip()

def extract_text(file_storage):
    filename = file_storage.filename.lower()
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    file_storage.save(save_path)

    if filename.endswith(".pdf"):
        return extract_text_from_pdf(save_path)
    elif filename.endswith(".docx"):
        return extract_text_from_docx(save_path)
    elif filename.endswith(".txt"):
        with open(save_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    else:
        raise ValueError("Unsupported file format")
        
@app.route("/upload_resume", methods=["POST"])
def upload_resume():
    if "resume" not in request.files:
        return jsonify(success=False, error="No resume uploaded")

    file = request.files["resume"]
    job_description = request.form.get("job_description", "").strip()
    
    # save_path = os.path.join("resumes", file.filename)
    # os.makedirs("resumes", exist_ok=True)
    try:
        resume_text = extract_text(file)
        if not job_description:
            return jsonify(success=False, error="No job description provided."), 400
        if not resume_text:
            return jsonify(success=False, error="No resume provided.."), 400
        processor.set_resume_and_jobdescript(resume_text, job_description)
        # Optional: process/store the text for LLM use here
        return jsonify(success=True, resume_text=resume_text[:1000])  # Truncate for preview
    except Exception as e:
        return jsonify(success=False, error=str(e)), 500
    

    # Optionally analyze it or queue it for the AI interviewer here
    return jsonify(success=True)

# Run the app
# app.run(debug=True)


# Serve the frontend
@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
