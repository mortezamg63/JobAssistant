import openai
import fitz  # PyMuPDF
from pydantic import BaseModel, Field
from typing import List, Optional


def extract_text_from_pdf(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text


# class Education(BaseModel):
#     institution: str = Field(..., title='institution/university', description='the name of university or institution')
#     location: str = Field(None, title='address', description='address of the university or institution')
#     degree: str = Field(..., title='degree', 
#     dates: Optional[str] = None
#     gpa: Optional[str] = None

class Education(BaseModel):
    degree: str = Field(..., title="Degree", description="Name of the degree or qualification")
    field_of_study: str = Field(..., title="Field of Study", description="Major or main subject")
    institution: str = Field(..., title="Institution", description="Name of the educational institution")
    start_year: int = Field(..., title="Start Year", description="Year when studies began")
    end_year: Optional[int] = Field(None, title="End Year", description="Year when studies ended or expected to end")
    grade: Optional[str] = Field(None, title="Grade", description="GPA, honors, or classification")
    description: Optional[str] = Field(None, title="Description", description="Additional details or achievements")

class Skills(BaseModel):
    category: str
    name: str


class Experience(BaseModel):
    job_title: str = Field(..., description="Title or position held")
    company: str = Field(..., description="Name of the company or organization")
    location: Optional[str] = Field(None, description="Location of the job (city, country)")
    start_date: str = Field(..., description="Start date (e.g., '2022-01' or 'Jan 2022')")
    end_date: Optional[str] = Field(None, description="End date or 'Present' if currently employed")
    description: Optional[str] = Field(None, description="Brief description of responsibilities and achievements")
   achievements: Optional[List[str]] = Field(None, description="List of notable achievements in this role")

class Projects(BaseModel):
    name: Optional[str]
    link: Optional[str] = None
    additiona_link: Optional[str] = None
    desc: str
    tech_skills: Optional[str] = None


class Project(BaseModel):
    name: str = Field(..., description="Name or title of the project")
    description: Optional[str] = Field(None, description="Brief summary of the project")
    technologies: Optional[List[str]] = Field(None, description="List of technologies, tools, or languages used")
    role: Optional[str] = Field(None, description="Your role or responsibility in the project")
    start_date: Optional[str] = Field(None, description="Project start date (e.g., '2023-01' or 'Jan 2023')")
    end_date: Optional[str] = Field(None, description="Project end date or 'Present' if ongoing")
    url: Optional[str] = Field(None, description="Link to the project (e.g., GitHub, website)")
    achievements: Optional[List[str]] = Field(None, description="Notable outcomes or accomplishments")

class Publication(BaseModel):
    title: str = Field(..., title="Title", description="The title of the publication")
    authors: List[str] = Field(..., title="Authors", description="List of author names")
    journal: Optional[str] = Field(None, title="Journal", description="Journal or venue name")
    year: int = Field(..., title="Year", description="Year of publication")
    volume: Optional[str] = Field(None, title="Volume", description="Volume number")
    issue: Optional[str] = Field(None, title="Issue", description="Issue number")
    pages: Optional[str] = Field(None, title="Pages", description="Page range")
    doi: Optional[str] = Field(None, title="DOI", description="Digital Object Identifier")
    url: Optional[str] = Field(None, title="URL", description="Link to the publication")
    abstract: Optional[str] = Field(None, title="Abstract", description="Summary of the publication")
    keywords: Optional[List[str]] = Field(None, title="Keywords", description="List of keywords")
    publisher: Optional[str] = Field(None, title="Publisher", description="Name of the publisher")


class Award(BaseModel):
    name: str = Field(..., description="Name of the award or honor")
    issuer: Optional[str] = Field(None, description="Organization or institution that granted the award")
    date: Optional[str] = Field(None, description="Date received (e.g., '2024-05' or 'May 2024')")
    description: Optional[str] = Field(None, description="Brief description or reason for the award")
    url: Optional[str] = Field(None, description="Link to more information about the award (if applicable)")

class AdditionalSection(BaseModel):
    section_title: str = Field(..., description="Title of the additional section (e.g., 'Certifications', 'Languages')")
    items: List[str] = Field(..., description="List of items or entries in this section")
    description: Optional[str] = Field(None, description="Optional description for the section")

    
class Resume(BaseModel):
    name: str
    location: str
    email: str
    phone: str
    linkedin: Optional[str]
    github: Optional[str]
    education: List[Education]
    skills: List[Skills]
    experience: Optional[List[str]]
    projects: Optional[List[str]]
    publications: Optional[List[str]]

def extract_resume_with_gpt(text: str) -> Resume:
    system_message = {
        "role": "system",
        "content": "You are an AI that converts resumes into structured JSON format for Pydantic parsing."
    }

    user_message = {
        "role": "user",
        "content": f"""Extract structured resume information from the following text and return valid JSON for this model:
