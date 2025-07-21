import os
import re
from PyPDF2 import PdfReader
from docx import Document

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
        # import pdb; pdb.set_trace()
        return header_html, sections_data, resume_text


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


    def parse_resume_with_openai(self, resume_text: str) -> Optional[Resume]:
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
        
        print('------ before calling openai --------')
        response = openai.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=4096,
            temperature=0,
            response_format=Resume,
        )
        print('------ after calling openai --------')
        import pdb; pdb.set_trace()
        output = response.choices[0].message.parsed
       
        return output
        # return sections

    # def convert_resume_to_list(self, resume_obj):
    #     output2 = []
    #     idx = 0
    #     for section in resume_obj.sections:
    #         for item in section.items:
    #             html = ""
    #             if section.section_name.lower() == "technical skills":
    #                 if item.details:
    #                     html = f"<p>{item.title}: {', '.join(item.details)}</p>"
    #             else:
    #                 if item.title:
    #                     html += f"<p>{item.title}</p>"
    #                 if item.details:
    #                     html += "<ul>" + "".join(f"<li>{d}</li>" for d in item.details) + "</ul>"
    
    #             entry = {
    #                 "id": idx, #uuid.uuid4().int % (10**6),  # shortened UUID
    #                 "section": section.section_name,
    #                 "subtitle": item.subtitle or "",
    #                 "html": html
    #             }
    #             output2.append(entry)
    #             idx+=1
    #     return output2

    def convert_resume_to_list(self,resume: Resume) -> List[Dict[str, Any]]:
        output = []
        id_counter = 0
        for section in resume.sections:
            if section.section_name.lower() == "technical skills":
                html_parts = []
                for item in section.items:
                    if item.details:
                        html_parts.append(
                            f"<p>{item.title}: {', '.join(item.details)}</p>"
                        )
                output.append({
                    "id": id_counter,
                    "section": section.section_name,
                    "subtitle": "Technical Skills",
                    "html": "".join(html_parts)
                })
                id_counter += 1
            else:
                for item in section.items:
                    html_parts = []
                    if item.title:
                        html_parts.append(f"<p>{item.title}</p>")
                    if item.details:
                        html_parts.append("<ul>")
                        for d in item.details:
                            html_parts.append(f"<li>{d}</li>")
                        html_parts.append("</ul>")
                    date_str = ""
                    if item.start_date or item.end_date:
                        date_str = f"  {item.start_date} – {item.end_date}".strip()
                    subtitle = item.subtitle.strip() if item.subtitle else ""
                    if subtitle and date_str:
                        subtitle += f"  {date_str}"
                    elif date_str:
                        subtitle = date_str
                    output.append({
                        "id": id_counter,
                        "section": section.section_name,
                        "subtitle": subtitle,
                        "html": "".join(html_parts)
                    })
                    id_counter += 1
        return output

                

    def parse(self,filepath):
        resume_text = self.extract_text_from_pdf(filepath)#'/home/mory/jobProject/resumeBuilder2/uploads/Mory_Gharasuie_resume.pdf')
        pydantic_output = self.parse_resume_with_openai(resume_text)
        # import pdb; pdb.set_trace()
        list_output = self.convert_resume_to_list(pydantic_output)
        import numpy as np
        return 'Header HTML', list_output, pydantic_output, resume_text