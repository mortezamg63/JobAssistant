from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import fitz  # PyMuPDF
from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv(override=True)
api_key = os.getenv('OPENAI_API_KEY')

def extract_text_from_pdf(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    return "\n".join(page.get_text() for page in doc)

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

def parse_resume_with_openai(resume_text: str) -> Optional[Resume]:
    openai = OpenAI(api_key=api_key)
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

def resume_to_markdown(resume):
    md = []
    for section in resume.sections:
        md.append(f"## {section.section_name}\n")
        for item in section.items:
            # Title and subtitle
            line = f"**{item.title}**"
            if item.subtitle:
                line += f", *{item.subtitle}*"
            # Dates
            if item.start_date or item.end_date:
                dates = []
                if item.start_date:
                    dates.append(item.start_date)
                if item.end_date:
                    dates.append(item.end_date)
                line += f" ({' - '.join(dates)})"
            md.append(line)
            # Details
            if item.details:
                for detail in item.details:
                    md.append(f"- {detail}")
            # Extra fields
            if item.extra:
                for k, v in item.extra.items():
                    md.append(f"  - **{k.capitalize()}**: {v}")
            md.append("")  # Blank line for spacing
    return "\n".join(md)


resume = extract_text_from_pdf('/home/mory/jobProject/resumeBuilder2/uploads/Mory_Gharasuie_resume.pdf')
output = parse_resume_with_openai(resume)
print(resume_to_markdown(output))  # Show as markdown

