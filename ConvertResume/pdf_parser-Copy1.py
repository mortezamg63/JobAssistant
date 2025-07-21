import os
import re
from PyPDF2 import PdfReader
from docx import Document

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import fitz  # PyMuPDF
from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv(override=True)


class ResumeItem(BaseModel):
    title: str
    subtitle: Optional[str]
    start_date: Optional[str]
    end_date: Optional[str]
    details: Optional[List[str]]
    extra: Optional[Dict[str, Any]]

class ResumeSection(BaseModel):
    section_name: str
    items: List[ResumeItem]

class Resume(BaseModel):
    sections: List[ResumeSection]


class ResumeParser_OpenAI:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        doc = fitz.open(pdf_path)
        return "\n".join(page.get_text() for page in doc)


    def parse_resume_with_openai(resume_text: str) -> Optional[Resume]:
    openai = OpenAI(api_key=self.api_key)
    # openai.api_key = openai_api_key
    prompt = f"""
You are an expert resume parser. Given this resume text, extract all information into the following JSON schema: {Resume.schema_json(indent=2)}
Resume Text:
\"\"\"
{resume_text}
\"\"\"
Return only the JSON.
"""
    response = openai.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4096,
        temperature=0,
        response_format=Resume,
    )
    output = response.choices[0].message.parsed
    # json_str = response['choices'][0]['message']['content']
    # import json
    # try:
    #     data = json.loads(json_str)
    #     return Resume.parse_obj(data)  # This will create ResumeSection and ResumeItem objects
    # except (json.JSONDecodeError, ValidationError) as e:
    #     print("Parsing error:", e)
    #     return None
    return output

    def parse(filepath:str):
        resume = extract_text_from_pdf(filepath)#'/home/mory/jobProject/resumeBuilder2/uploads/Mory_Gharasuie_resume.pdf')
        return parse_resume_with_openai(resume)
        



class ResumeParser:
    # date‐range regex components
    MONTH = r'(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|' \
            r'Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|' \
            r'Nov(?:ember)?|Dec(?:ember)?)'
    YEAR  = r'\d{4}'
    DATE  = rf'{MONTH}\s+{YEAR}'
    RANGE = rf'{DATE}\s*[–—-]\s*(?:Present|{DATE})'

    def __init__(self, known_headings=None):
        self.known_headings = known_headings or [
            'Technical Skills','Experience','Education','Projects','Publications'
        ]
        # compile once
        self._re_range = re.compile(self.RANGE)
        self._re_year_range = re.compile(r'\(\s*\d{4}\s*[–-]\s*\d{4}\s*\)')
        self._re_degree = re.compile(r'\b(Bachelor|Master|Ph\.?D|Doctor|Dissertation)\b', re.IGNORECASE)
        

    @staticmethod
    def _parse_pdf_lines(path):
        reader = PdfReader(path)
        lines = []
        for p in reader.pages:
            txt = p.extract_text() or ''
            lines.extend(txt.splitlines())
        return lines

    @staticmethod
    def _parse_docx_lines(path):
        doc = Document(path)
        return [p.text for p in doc.paragraphs if p.text.strip()]

    def is_main_heading(self, line: str) -> bool:
        t = line.strip()
        # exact match known headings
        if any(t.lower() == h.lower() for h in self.known_headings):
            return True
        # all‐caps short line
        words = t.split()
        if 1 < len(words) <= 5 and re.fullmatch(r'[A-Z0-9 &]+', t):
            return True
        return False

    def split_by_main_headings(self, lines: list[str]) -> list[tuple[str, list[str]]]:
        blocks, curr, buf = [], None, []
        for raw in lines:
            if self.is_main_heading(raw):
                if curr:
                    blocks.append((curr, buf))
                curr, buf = raw.strip(), []
            else:
                if curr:
                    buf.append(raw)
        if curr:
            blocks.append((curr, buf))
        return blocks

    def is_subsection(self, line: str) -> bool:
        t = line.strip()
        # a) date‐range like “Jan 2020 – Present”
        if self._re_range.search(t):
            return True
        # b) parenthesized year range “(2020-2022)”
        if self._re_year_range.search(t):
            return True
        # c) explicit degree/advisor keywords
        if self._re_degree.search(t):
            return True
        # d) Title Case moderate length
        words = t.split()
        if 1 < len(words) <= 7 and all(w[0].isupper() for w in words if w):
            return True
        return False

    def split_into_subsections(self, lines: list[str]) -> list[tuple[str, list[str]]]:
        subs, curr, buf = [], None, []
        for raw in lines:
            if self.is_subsection(raw):
                if curr is not None:
                    subs.append((curr, buf))
                curr, buf = raw.strip(), []
            else:
                buf.append(raw)
        if curr is not None:
            subs.append((curr, buf))
        else:
            # no subsections detected → treat entire block as one
            subs = [(None, lines)]
        return subs

    def build_html_from_lines(self, lines: list[str]) -> str:
        html, in_list = [], False
        for raw in lines:
            s = raw.strip()
            if s.startswith(('•','-','*','–')):
                if not in_list:
                    html.append('<ul>'); in_list = True
                item = s.lstrip('•-*– ').strip()
                html.append(f'<li>{item}</li>')
            else:
                if in_list:
                    html.append('</ul>'); in_list = False
                if s:
                    html.append(f'<p>{s}</p>')
        if in_list:
            html.append('</ul>')
        return ''.join(html)

    def parse(self, filepath: str) -> tuple[str, list[dict], str]:
        """
        Returns (header_html, sections_data, full_resume_text)
        """
        ext = os.path.splitext(filepath)[1].lower()
        raw = (self._parse_pdf_lines(filepath)
               if ext == '.pdf'
               else self._parse_docx_lines(filepath))

        # full text
        resume_text = "\n".join(raw)

        # header before first main heading
        idx = next((i for i,l in enumerate(raw) if self.is_main_heading(l)), len(raw))
        header_html = self.build_html_from_lines(raw[:idx])

        # split into sections + subsections
        sections_data = []
        count = 0
        for heading, block in self.split_by_main_headings(raw[idx:]):
            for sub_title, body in self.split_into_subsections(block):
                subtitle = sub_title or heading
                html_body = self.build_html_from_lines(body)
                sections_data.append({
                    'id': count,
                    'section': heading,
                    'subtitle': subtitle,
                    'html': html_body
                })
                count += 1

        return header_html, sections_data, resume_text


    def ChatGPT_parse(self, filepath:str):
        
