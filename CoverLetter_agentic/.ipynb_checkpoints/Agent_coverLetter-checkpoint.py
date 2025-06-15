from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
# import matplotlib.pyplot as plt
# %matplotlib inline
from typing import List, Sequence
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import END, MessageGraph
import json

load_dotenv()

system_prompt = """
You are a highly skilled and professional assistant specialized in writing tailored, impactful cover letters for job applications. Your primary role is to generate personalized cover letters by analyzing both the user's resume and the specific job posting. You must ensure that each letter is aligned with the job requirements and company culture, and presents the candidate in the most compelling and authentic light.

When crafting the cover letter, you must strictly adhere to the following principles:

    Customization: Every cover letter must be uniquely tailored to the job and company. Do not use generic templates. Use insights from the job posting and company background to make the letter specific and relevant.

    Alignment with Role & Culture: Clearly demonstrate how the user’s background, skills, and experience align with both the role and the company's mission, values, and culture.

    Highlight Key Qualifications: Emphasize the user’s most relevant skills, achievements, and experiences that match the job description. Show measurable impact where possible.

    Elaboration Beyond the Resume: Expand on important resume points with depth and context. Add personal insights that aren’t found in the resume.

    Showcase Personality & Story: Let the user’s strengths, career motivations, and personality come through. Include meaningful anecdotes or brief stories that reflect their competencies and character.

    Express Genuine Interest: Clearly communicate enthusiasm for the position and organization. Make it evident that the user has taken the time to learn about the company.

    Professional Formatting: Format the letter like a formal business letter. Include contact information, date, a greeting, an opening paragraph, middle content, a closing paragraph, and a polite sign-off.

    Clarity and Brevity: Keep the letter concise—ideally one page, using clear language and professional tone. Structure it into three core sections: introduction, body, and conclusion.

    Strong Opening: Begin with a compelling paragraph that names the job title, source of the posting, and the reason for interest in the role and company.

    Focused Body Paragraph(s): Provide a focused narrative on key skills and achievements. Use quantifiable results where applicable. Connect the user’s background with the job responsibilities.

    Effective Closing: Summarize the user’s value proposition, restate interest, offer availability, and thank the reader for their time.

    Professional Sign-off: End with a courteous and professional closing (e.g., “Sincerely”) followed by the user’s name.

    Address Resume Concerns: Where applicable, briefly and professionally address employment gaps, career transitions, or other atypical aspects of the resume.

    Proofreading: Your output must be free of grammar, punctuation, and spelling errors. Ensure clear, fluid, and natural English.

You must act as a professional cover letter writer with a deep understanding of modern hiring practices and an ability to strategically present job candidates in the best possible light. Be informative, concise, persuasive, and precise.

- Do **not invent** experiences, qualifications, or achievements that are not present in the resume.
- All claims must be **grounded in the resume** and **relevant to the job description**.

"""


opening_paragraph_prompt = """

Here is my resume: {resume}

here is the job description: {job_description}

Please generate a compelling opening paragraph for their cover letter that makes a strong first impression and follows best practices.

Your output must accomplish the following objectives:

    Mention the specific job title the user is applying for and where the job posting was found (e.g., Indeed, LinkedIn, the company’s careers page).

    Express genuine interest in the specific role and the company. Reflect the user’s understanding of the company’s mission, product, reputation, or goals to show they’ve done their research. Avoid generic language.

    Introduce the candidate professionally, providing a concise summary of their background (e.g., years of experience, field of expertise, or industry).

    Explain how the position aligns with the candidate’s career goals, showing thoughtfulness and long-term motivation.

    If applicable, briefly acknowledge career transitions or employment gaps, including circumstances like COVID-related layoffs—but the focus should remain on enthusiasm and fit for the position.

    Write in a way that quickly appeals to the hiring manager, keeping the tone enthusiastic, authentic, and professional.

Examples to guide your tone and structure:

    “I’m excited to apply for the [Job Title] position at [Company Name] I found on [Job Board]. I admire your work in [Company Specialty or Initiative], and I believe my background in [Relevant Experience] makes me a strong match. This role aligns perfectly with my goal to [Career Goal], and I’d be thrilled to contribute to your team.”

    “I’m applying for the [Job Title] role at [Company Name], as advertised on [Job Platform]. With [X years] of experience in [Industry/Function], I bring a [mention one or two relevant strengths]. I'm passionate about [relevant motivation], and I see this opportunity as a natural next step in my career.”

Use concise, engaging language and maintain a professional but approachable tone. Focus only on the opening paragraph of the cover letter. Again, only write the opening paragraph not all paragraphs

Begin writing the opening paragraph now.

[Opening Paragraph]:
"""

middle_paragraph_prompt = """

Here is my resume: {resume}

here is the job description: {job_description}


Please write the middle paragraph(s) of a cover letter. In this section, your primary goal is to showcase the candidate’s qualifications and achievements in a way that directly connects with the job requirements and the company’s needs.

Your output must satisfy the following instructions:

    Elaborate on relevant experience from the resume, going beyond repetition. Add meaningful context, describe the candidate’s role and contributions in past positions, and demonstrate their value through storytelling.

    Highlight one or two key achievements or skills most relevant to the job. These should be specific, with measurable results where possible (e.g., “increased retention by 20%,” “led a cross-functional team of 8,” “reduced processing time by 40%”).

    Use job description keywords naturally in your writing, especially those that match the user’s strengths and responsibilities. This improves relevance and helps the letter pass Applicant Tracking Systems (ATS).

    Tie achievements and qualifications to company needs. Show how the candidate’s experience makes them a great match for the company’s role, values, mission, or industry challenges.

    If applicable, clarify any career transitions or gaps professionally and briefly, especially if the gap extends beyond 6 months. If the candidate is transitioning careers, emphasize transferable skills and how they meet the requirements of the role.

    Keep the content focused, engaging, and concise—typically no more than one or two short paragraphs.

Example inspiration:

    “In my most recent role as a data analyst at [Company], I led a project that automated the reporting pipeline, reducing processing time by 35% and enabling real-time analytics. My proficiency in Python, SQL, and Tableau aligns closely with the technical skills listed in your posting.”

    “I’ve developed a strong foundation in project coordination through managing multi-phase software deployments for clients in healthcare. My ability to communicate effectively across teams and manage stakeholder expectations has been key to delivering solutions on time and under budget.”

Your writing should be precise, professional, and results-oriented. This is the part of the letter where the candidate proves their value through evidence.

Focus only on writing the middle paragraph(s) of the cover letter.

[middle Paragraph]:"""


closing_paragraph_prompt = """

Here is my resume: {resume}

here is the job description: {job_description}

Please  generate a strong closing paragraph that leaves a positive final impression and motivates the hiring manager to proceed with the candidate.

Your output must include the following elements:

    Summarize qualifications: Reiterate why the candidate is a strong fit for the position. Optionally, you may include one final achievement, strength, or anecdote not already covered in the body of the letter. If the user is transitioning careers, you may highlight transferable skills that align with the new role.

    Express continued interest: Restate the user’s enthusiasm for the role and the company. Show eagerness to move forward in the process and interest in contributing to the team.

    Indicate next steps and availability: Clearly state how the employer can reach the user (email and/or phone), and optionally mention availability for an interview or discussion.

    Thank the reader: Politely thank the hiring manager for reviewing the application and considering the candidate.

    Use a professional sign-off: End with a formal closing such as “Sincerely,” followed by the user’s full name.

Tone and format: Keep the paragraph brief, positive, and professional. Aim for a tone that is confident yet humble, and inviting without being overly casual.

Example inspiration:

    “Thank you for taking the time to review my application. I’m excited about the opportunity to bring my skills in [relevant skill] to the [Company Name] team. I would welcome the chance to discuss this role further and can be reached at [email] or [phone]. I look forward to speaking with you. Sincerely, [Your Name]”

    “My commitment to [relevant goal] and my background in [relevant experience] make me confident I can contribute meaningfully to your team. Thank you for considering my application. I’m eager to learn more about the [Job Title] role at [Company Name] and am available for an interview at your convenience. Sincerely, [Your Name]”

Focus exclusively on generating the closing paragraph of the cover letter.

write the closing paragraph now.

[closing Paragraph]:
"""


critique_prompt = """
You are an expert cover letter reviewer and career writing coach. Your task is to **critically evaluate** the following generated cover letter for clarity, relevance, professionalism, and alignment with the user's resume and the job description.

Your critique must follow these guidelines:

---

**📌 Opening Paragraph:**
- Does it mention the specific job title and where the job was found?
- Does it express genuine interest in the company and role, showing evidence of research?
- Does it briefly introduce the candidate and connect the role to their career goals?

**📌 Middle Paragraph(s):**
- Does it elaborate on relevant experiences from the resume (not just repeat them)?
- Are specific, measurable achievements or examples provided?
- Are keywords and skills from the job description used appropriately?
- Is there a clear match between the candidate’s background and the company’s needs?
- Are any transitions or gaps explained appropriately if relevant?

**📌 Closing Paragraph:**
- Does it restate the candidate’s interest and value clearly?
- Does it include contact details and availability for next steps?
- Is there a proper thank-you and professional sign-off?

---

**🚫 NO HALLUCINATIONS:**
- Do **not invent** experiences, qualifications, or achievements that are not present in the resume.
- All claims must be **grounded in the resume** and **relevant to the job description**.

---

**Your Task:**
Provide a detailed critique of the cover letter. Highlight strengths, identify weaknesses, and suggest **specific, actionable revisions** that improve the letter’s alignment with the resume, job description, and professional standards.

Here is the generated cover letter:
-------------------------------
{cover_letter}
-------------------------------

Begin your critique below:
"""

companyInfo_system_prompt = """
You are an intelligent assistant specialized in extracting structured information from job postings.
Your task is to analyze job descriptions and extract key company information in a structured format.

If any information is **missing or unclear**, return "N/A" for that field. Do not guess or hallucinate.
Return the result in **JSON format** based on the following schema:

- company_name: Name of the company offering the job.
- company_address: Address of the company, including city and/or state if available.
"""

companyInfo_human_prompt = """
Here is the job description:

--------------------------
{job_description}
--------------------------

Please extract the company name and address according to the schema described in the system prompt.
If either field is not found, return "N/A" for that field.
"""

class CompanyInfo(BaseModel):
    company_name: str
    company_address: str

class UserInfo(BaseModel):
    fullname: str
    email: str
    github_link: str
    linkedin_link: str
    
class Agent_coverLetter:

    companyInfo_parser = PydanticOutputParser(pydantic_object=CompanyInfo)

    
    def __init__(self, job_description=None, resume=None):
        # import pdb; pdb.set_trace()
        if resume is None:
            with open('resume.txt', "r") as f:
                self.myresume = f.read()
        else:
            self.myresume = resume
            
        if job_description is None:
            with open('job_desc.txt', "r") as f:
                self.job_desc = f.read()
        else:
            self.job_desc=job_description

        self.generation_opening = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", opening_paragraph_prompt.format(resume=self.myresume, job_description=self.job_desc))
        ])
        
        self.generation_middle = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", middle_paragraph_prompt.format(resume=self.myresume, job_description=self.job_desc))
        ])
        
        self.generation_closing = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", closing_paragraph_prompt.format(resume=self.myresume, job_description=self.job_desc))
        ])
        
        self.reflection_prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human",critique_prompt )
        ])

        self.generation_companyInfo_prompt = ChatPromptTemplate.from_messages([
            ("system", companyInfo_system_prompt),
            ("human", companyInfo_human_prompt)#+"\n\n"+self.companyInfo_parser.get_format_instructions())
            ])

        self.initialChains()
        
        

        

    def initialChains(self):
        self.llm=ChatOpenAI(model='gpt-4o-mini') # initializing LLM (gpt 3.5 turbo)
        self.generate_opening_chain = self.generation_opening | self.llm
        self.generate_middle_chain = self.generation_middle | self.llm
        self.generate_closing_chain = self.generation_closing | self.llm
        self.reflect_chain = self.reflection_prompt | self.llm
        self.companyInfo_chain = self.generation_companyInfo_prompt | self.llm | self.companyInfo_parser


    def generation_node_companyInfo(self,  state: Sequence[BaseMessage]):
        # import pdb; pdb.set_trace()
        result = self.companyInfo_chain.invoke({"job_description":self.job_desc}) 
        # self.companyName = result.company_name
        # self.companyAddress = result.company_address
        return [HumanMessage(content=result.json())]
        


        
    def generation_node_opening(self,state: Sequence[BaseMessage]):
        # import pdb; pdb.set_trace()
        result = self.generate_opening_chain.invoke({"messages":state}) 
        return result
    
    
    
    def generation_node_middle(self, state: Sequence[BaseMessage]):
        # import pdb; pdb.set_trace()
        result = self.generate_middle_chain.invoke({"messages":state}) 
        return result
    
    
    
    def generation_node_closing(self, state: Sequence[BaseMessage]):
        # import pdb; pdb.set_trace()
        result = self.generate_closing_chain.invoke({"messages":state}) 
        return result #{'cover_letter': result.content}
    
    def reflection_node(self, state: dict):#messages: Sequence[BaseMessage]):
        # import pdb; pdb.set_trace()
        cover_letter_text = state[-3].content+'\n'+state[-2].content+'\n'+state[-1].content
        filled_prompt = critique_prompt.format(cover_letter=cover_letter_text)
        return self.reflect_chain.invoke([HumanMessage(content=filled_prompt)])

    def should_continue(self, state: List[BaseMessage]): # It's very simple reasoning
        if len(state)>0:
            return 'gen_companyInfo'
        else:
            return 'reflection'


    def build_Graph(self):
        builder = MessageGraph()
        builder.add_node('gen_companyInfo',self.generation_node_companyInfo)
        builder.add_node('gen_opening', self.generation_node_opening)
        builder.add_node('gen_middle', self.generation_node_middle)
        builder.add_node('gen_closing', self.generation_node_closing)
        builder.add_node('reflection', self.reflection_node)
        
        builder.set_entry_point('gen_opening')
        
        # builder.add_edge('gen_companyInfo', 'gen_opening')
        builder.add_edge('gen_opening', 'gen_middle')
        builder.add_edge('gen_middle', 'gen_closing')
        builder.add_conditional_edges('gen_closing', self.should_continue)
        builder.add_edge('reflection', 'gen_opening')
        builder.add_edge('gen_companyInfo', END)
        graph = builder.compile()
        return graph


    def run(self):
        inputs = HumanMessage(content="""Please write my cover letter w.r.t job description and my resume""")
        graph = self.build_Graph()
        # print(graph.get_graph().draw_mermaid())
        # graph.get_graph().print_ascii()
        response = graph.invoke(inputs)
        # import pdb; pdb.set_trace()
        self.coverLetter =  'Dear Hiring Manager \n\n'+ response[1].content+'\n\n'+response[2].content+'\n\n'+response[3].content
        companyInfo_dict = json.loads(response[-1].content)
        # print("\n\n"+companyInfo_dict['company_name']+', '+ companyInfo_dict['company_address']+'\n\n\n'+self.coverLetter)
        # print(response[1].content)
        return companyInfo_dict['company_name'], companyInfo_dict['company_address'], self.coverLetter
        
# if __name__ == "__main__":
#     agent = Agent_coverLetter()
#     print(agent.run())