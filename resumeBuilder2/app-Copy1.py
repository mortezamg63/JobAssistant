import os
import re
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import PyPDF2
from docx import Document

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# In-memory store of all subsections
sections_data = []

# Primary headings in your resume
KNOWN_HEADINGS = [
    'Technical Skills',
    'Experience',
    'Education',
    'Projects',
    'Publications'
]

def split_by_main_headings(lines):
    """Group all lines under each top-level heading."""
    blocks = []
    curr_title = None
    curr = []
    for raw in lines:
        txt = raw.strip()
        if txt.lower() in [h.lower() for h in KNOWN_HEADINGS]:
            if curr_title is not None:
                blocks.append((curr_title, curr))
            curr_title = next(h for h in KNOWN_HEADINGS if h.lower() == txt.lower())
            curr = []
        else:
            if curr_title is not None:
                curr.append(raw)
    if curr_title is not None:
        blocks.append((curr_title, curr))
    return blocks

def split_into_subsections(lines):
    """
    Split a block into subsections every time we see a line with '|'.
    """
    subs = []
    curr_title = None
    curr = []
    for raw in lines:
        if '|' in raw:
            if curr_title is not None:
                subs.append((curr_title, curr))
            curr_title = raw.strip()
            curr = []
        else:
            curr.append(raw)
    if curr_title is not None:
        subs.append((curr_title, curr))
    if not subs:
        return [(None, lines)]
    return subs

def build_html(lines):
    """Convert raw lines into HTML with <p> and <ul><li>."""
    html_parts = []
    bullets = []

    def flush_bullets():
        nonlocal bullets
        if bullets:
            html_parts.append('<ul>')
            for b in bullets:
                html_parts.append(f'<li>{b}</li>')
            html_parts.append('</ul>')
            bullets = []

    for raw in lines:
        s = raw.strip()
        if s.startswith(('•','-','*','–')):
            bullets.append(s.lstrip('•-*– ').rstrip())
        else:
            flush_bullets()
            if s:
                html_parts.append(f'<p>{s}</p>')
    flush_bullets()
    return '\n'.join(html_parts)

def parse_pdf(path):
    rdr = PyPDF2.PdfReader(path)
    lines = []
    for pg in rdr.pages:
        txt = pg.extract_text()
        if txt:
            lines.extend(txt.splitlines())
    return lines

def parse_docx(path):
    doc = Document(path)
    return [p.text for p in doc.paragraphs if p.text.strip()]

def get_next_id():
    return max((s['id'] for s in sections_data), default=-1) + 1

def generate_sections(raw_lines):
    """
    1) Split raw_lines into main blocks by KNOWN_HEADINGS
    2) Within each block, split by any '|' line into subsections
    3) Build HTML for each body
    """
    secs = []
    counter = 0
    blocks = split_by_main_headings(raw_lines)
    for heading, block_lines in blocks:
        subs = split_into_subsections(block_lines)
        for title, body in subs:
            subtitle = title if title else heading
            html = build_html(body)
            secs.append({
                'id': counter,
                'section': heading,
                'subtitle': subtitle,
                'html': html
            })
            counter += 1
    return secs

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    global sections_data
    f = request.files.get('file')
    if not f:
        return jsonify({'error': 'No file provided'}), 400

    _, ext = os.path.splitext(f.filename.lower())
    if ext not in ('.pdf', '.docx', '.doc'):
        return jsonify({'error': 'Unsupported file type'}), 400

    save_path = os.path.join(UPLOAD_FOLDER, f.filename)
    f.save(save_path)

    raw = parse_pdf(save_path) if ext == '.pdf' else parse_docx(save_path)
    sections_data = generate_sections(raw)
    return jsonify({'sections': sections_data}), 200

@app.route('/sections', methods=['GET'])
def list_sections():
    return jsonify(sections_data), 200

@app.route('/sections', methods=['POST'])
def create_section():
    global sections_data
    data = request.get_json() or {}
    section = data.get('section')
    subtitle = data.get('subtitle')
    html = data.get('html', '')
    new_id = get_next_id()
    sec = {'id': new_id, 'section': section, 'subtitle': subtitle, 'html': html}
    sections_data.append(sec)
    return jsonify(sec), 201

@app.route('/sections/<int:sec_id>', methods=['PUT'])
def update_section(sec_id):
    data = request.get_json() or {}
    for sec in sections_data:
        if sec['id'] == sec_id:
            sec['html'] = data.get('html', sec['html'])
            return jsonify(sec), 200
    return jsonify({'error': 'Section not found'}), 404

@app.route('/sections/<int:sec_id>', methods=['DELETE'])
def delete_section(sec_id):
    global sections_data
    for i, sec in enumerate(sections_data):
        if sec['id'] == sec_id:
            sections_data.pop(i)
            return '', 204
    return jsonify({'error': 'Section not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
