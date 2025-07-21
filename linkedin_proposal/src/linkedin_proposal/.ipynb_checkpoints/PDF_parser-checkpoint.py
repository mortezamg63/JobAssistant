import os
import re
from pypdf import PdfReader
# from docx import Document

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import pymupdf as fitz  # PyMuPDF
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
        import pdb; pdb.set_trace()
        # print("openAI key: ", self.api_key)
        response = openai.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=4096,
            temperature=0,
            response_format=Resume,
        )
        print('------ after calling openai --------')
        # import pdb; pdb.set_trace()
        output = response.choices[0].message.parsed
       
        return output
       
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