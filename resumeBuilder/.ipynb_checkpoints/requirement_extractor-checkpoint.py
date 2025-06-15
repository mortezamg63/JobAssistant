from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import Agent, Runner, trace, function_tool, OpenAIChatCompletionsModel, input_guardrail, GuardrailFunctionOutput
from typing import Dict
import sendgrid
import os
from sendgrid.helpers.mail import Mail, Email, To, Content
from pydantic import BaseModel






class ResumeBuilder:
    def __init__(self):
        load_dotenv()
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if openai_api_key:
            print(f"OpenAI API Key exists and begins {openai_api_key[:8]}")
        else:
            print("OpenAI API Key not set")

        self.system_prompt = """You are a highly capable Career Coach and Resume Optimization Assistant.  
            When given a candidate’s current resume and a target job description, you will:
            
            1. **Analyze the job description** to identify all the critical keywords, skills, certifications, and experience requirements the employer is seeking.  
            2. **Categorize** these into sections (e.g. Technical Skills, Soft Skills, Tools & Technologies, Certifications, Domain Knowledge).  
            3. **Map** each category back to the candidate’s resume, highlighting which competencies are already well represented and which are missing or under-emphasized.  
            4. **Produce**  
               a. A concise, prioritized list of keywords/skills the candidate must emphasize or add.  
               b. Actionable suggestions for how to weave each missing or under-emphasized keyword into existing bullet points or to add new bullet points—using strong, achievement-oriented language.  
            5. Always format your output in a clear, structured way (e.g. numbered lists, headers) so the candidate can easily update their resume.
            """
        resumeMatch_Agent = Agent(
        name="Professional Sales Agent",
        instructions=self.system_prompt,
        model="gpt-4o-mini"
        )

        self.user_prompt = """Here is my current resume (in plain text or PDF-extracted text):
                    {RESUME}
                    
                    Here is the full job description for the position I’m targeting:
                    {JOB_DESCRIPTION}
                    
                    Please extract and categorize all the required keywords and skills from the job description, identify which ones I should emphasize or add to my resume, and give me concrete bullet-point rewrites or additions to ensure I’m using the right language to win this role.
                    """
        self.resume = self.job_description = None

        def getResume_JobDesc(self, resume, jobdesc):
            self.resume = resume
            
            
        