import os, re
from flask import Flask, request, jsonify, render_template, Response
from flask_cors import CORS
import PyPDF2
from docx import Document
from weasyprint import HTML as PDFGenerator

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

sections_data = []
header_html = ''

KNOWN_HEADINGS = ['Technical Skills', 'Experience', 'Education', 'Projects', 'Publications']

def split_by_main_headings(lines):
    blocks = []
    current_heading = None
    buffer = []

    for raw in lines:
        text = raw.strip()
        if text.lower() in (h.lower() for h in KNOWN_HEADINGS):
            if current_heading is not None:
                blocks.append((current_heading, buffer))
            # find the original-cased heading
            current_heading = next(h for h in KNOWN_HEADINGS if h.lower() == text.lower())
            buffer = []
        else:
            if current_heading is not None:
                buffer.append(raw)

    if current_heading is not None:
        blocks.append((current_heading, buffer))

    return blocks

def split_into_subsections(lines):
    subs = []
    sub_title = None
    buffer = []

    for raw in lines:
        if '|' in raw:
            if sub_title is not None:
                subs.append((sub_title, buffer))
            sub_title = raw.strip()
            buffer = []
        else:
            buffer.append(raw)

    if sub_title is not None:
        subs.append((sub_title, buffer))

    # if no '|' found at all, just return the entire block as one subsection
    return subs or [(None, lines)]

def build_html_from_lines(lines):
    parts = []
    bullets = []

    def flush_bullets():
        nonlocal bullets
        if bullets:
            parts.append('<ul>')
            for b in bullets:
                parts.append(f'<li>{b}</li>')
            parts.append('</ul>')
            bullets = []

    for raw in lines:
        s = raw.strip()
        if s.startswith(('•','-','*','–')):
            bullets.append(s.lstrip('•-*– '))
        else:
            flush_bullets()
            if s:
                parts.append(f'<p>{s}</p>')

    flush_bullets()
    return '\n'.join(parts)

def parse_pdf_lines(path):
    reader = PyPDF2.PdfReader(path)
    out = []
    for page in reader.pages:
        txt = page.extract_text()
        if txt:
            out.extend(txt.splitlines())
    return out

def parse_docx_lines(path):
    doc = Document(path)
    return [p.text for p in doc.paragraphs if p.text.strip()]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    global sections_data, header_html

    f = request.files.get('file')
    if not f:
        return jsonify({'error': 'No file provided'}), 400

    _, ext = os.path.splitext(f.filename.lower())
    if ext not in ('.pdf', '.docx', '.doc'):
        return jsonify({'error': 'Unsupported file type'}), 400

    save_path = os.path.join(UPLOAD_FOLDER, f.filename)
    f.save(save_path)

    raw_lines = (parse_pdf_lines(save_path)
                 if ext == '.pdf'
                 else parse_docx_lines(save_path))

    # 1) extract header (everything before the first main heading)
    first_heading_idx = next(
        (i for i, line in enumerate(raw_lines)
         if line.strip().lower() in (h.lower() for h in KNOWN_HEADINGS)),
        len(raw_lines)
    )
    header_html = build_html_from_lines(raw_lines[:first_heading_idx])

    # 2) split into subsections
    new_sections = []
    idx_counter = 0
    for heading, block in split_by_main_headings(raw_lines):
        for sub_title, body in split_into_subsections(block):
            subtitle = sub_title if sub_title else heading
            section_html = build_html_from_lines(body)
            new_sections.append({
                'id': idx_counter,
                'section': heading,
                'subtitle': subtitle,
                'html': section_html
            })
            idx_counter += 1

    sections_data = new_sections
    return jsonify({'sections': sections_data})

@app.route('/sections', methods=['GET'])
def list_sections():
    return jsonify(sections_data)

@app.route('/sections', methods=['POST'])
def create_section():
    global sections_data
    data = request.get_json() or {}
    new_id = max((s['id'] for s in sections_data), default=-1) + 1
    sec = {
        'id': new_id,
        'section': data.get('section'),
        'subtitle': data.get('subtitle'),
        'html': data.get('html', '')
    }
    sections_data.append(sec)
    return jsonify(sec), 201

@app.route('/sections/<int:sec_id>', methods=['PUT'])
def update_section(sec_id):
    data = request.get_json() or {}
    for s in sections_data:
        if s['id'] == sec_id:
            s['subtitle'] = data.get('subtitle', s['subtitle'])
            s['html']     = data.get('html', s['html'])
            return jsonify(s)
    return jsonify({'error': 'Section not found'}), 404

@app.route('/sections/<int:sec_id>', methods=['DELETE'])
def delete_section(sec_id):
    global sections_data
    for i, s in enumerate(sections_data):
        if s['id'] == sec_id:
            sections_data.pop(i)
            return '', 204
    return jsonify({'error': 'Section not found'}), 404

@app.route('/export', methods=['POST'])
def export_pdf():
    data = request.get_json() or {}
    sent_sections = data.get('sections', [])

    # regroup by main section
    sections_by_main = {}
    for s in sent_sections:
        sections_by_main.setdefault(s['section'], []).append(s)

    rendered = render_template(
        'export.html',
        header_html=header_html,
        sections_by_main=sections_by_main
    )

    pdf_bytes = PDFGenerator(string=rendered).write_pdf()
    return Response(
        pdf_bytes,
        mimetype='application/pdf',
        headers={'Content-Disposition': 'attachment; filename=resume.pdf'}
    )

if __name__ == '__main__':
    app.run(debug=True)
