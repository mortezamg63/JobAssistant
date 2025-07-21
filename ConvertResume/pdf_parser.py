
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
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=4096,
            temperature=0,
            response_format=Resume,
        )
        print('------ after calling openai --------')
        import pdb; pdb.set_trace()
        output = response.choices[0].message.parsed
       
        return output.sections
        # return sections

    def parse(self,filepath):
        resume_text = self.extract_text_from_pdf(filepath)#'/home/mory/jobProject/resumeBuilder2/uploads/Mory_Gharasuie_resume.pdf')
        return 'Header HTML', self.parse_resume_with_openai(resume_text), resume_text
        
        


