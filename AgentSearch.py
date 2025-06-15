# imports
import requests
from bs4 import BeautifulSoup
from IPython.display import Markdown, display
import os
import json
import requests
from googlesearch import search  # Free Google search library
from dotenv import load_dotenv
from openai import OpenAI
from IPython.display import Markdown, display, update_display
from urllib.parse import urlparse

load_dotenv(override=True)
api_key = os.getenv('OPENAI_API_KEY')

class Website:
    headers = {
 "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}
    def __init__(self, url):
        self.url = url
        response = requests.get(url, headers=self.headers)
        self.body = response.content
        soup = BeautifulSoup(self.body, 'html.parser')
        self.title = soup.title.string if soup.title else "No title found"
        if soup.body:
            for irrelevant in soup.body(["script", "style", "img", "input"]):
                irrelevant.decompose()
            self.text = soup.body.get_text(separator="\n", strip=True)
        else:
            self.text = ""
        links = [link.get('href') for link in soup.find_all('a')]
        self.links = [link for link in links if link]

    def get_contents(self):
        return f"Webpage Title:\n{self.title}\nWebpage Contents:\n{self.text}\n\n"
    
    

class SummarizationAgent:
    def __init__(self):
        self.link_system_prompt = "You are provided with a list of links found on a webpage. \
        You are able to decide which of the links would be most relevant to include in a brochure about the company, \
        such as links to an About page, or a Company page, or Careers/Jobs pages.\n"
        
        self.link_system_prompt += "You should respond in JSON as in this example:"
        self.link_system_prompt += """
        {
            "links": [
                {"type": "about page", "url": "https://full.url/goes/here/about"},
                {"type": "careers page": "url": "https://another.full.url/careers"}
            ]
        }
        """

        self.link_system_prompt = "You are provided with a list of links found on a webpage. \
        Your task is to determine which links are most relevant for finding job-related information, \
        including job postings, team structures, related projects, departments, company research, and company news. \
        Prioritize pages that provide context about the job role and its industry impact.\n"
        self.link_system_prompt += "You should respond in JSON as in this example:"
        self.link_system_prompt += """
                {
                    "links": [
                        {"type": "job posting", "url": "https://full.url/goes/here/job-title"},
                        {"type": "careers page", "url": "https://full.url/goes/here/careers"},
                        {"type": "team/department page", "url": "https://full.url/goes/here/team"},
                        {"type": "project/research page", "url": "https://full.url/goes/here/project"},
                        {"type": "company news", "url": "https://full.url/goes/here/news"}
                    ]
                }
        """

        self.system_prompt = "You are an assistant that searches for and extracts all available information related to a job posting from a company website. \
                Your goal is to gather as much detail as possible to help the user understand the job role, its responsibilities, \
                the projects it is related to, the team or department it belongs to, and any background about the company’s work in this area. Find anything that can be related to keywords in job description\
                Analyze relevant webpages, including careers, company projects, teams, and news, to provide a comprehensive understanding \
                of the job in its full context. Preserve all relevant text and descriptions while ensuring clarity and completeness. \
                Respond in Markdown format."

        load_dotenv(override=True)
        api_key = os.getenv('OPENAI_API_KEY')

        self.MODEL = 'gpt-4o-mini'
        self.openai = OpenAI()
        

    
    def generate_search_term(self, job_description):
        """Use OpenAI to generate an optimized search term based on the job description."""
        # V2
        prompt = f"""
                    Given the following job description, generate an optimized search term to find **relevant background information** about this role. 
                    Avoid returning direct job postings or career listings that repeat the job description.
                    
                    The search term should help find:
                    - **Company projects** related to this job role.
                    - **Industry focus and research** relevant to this field.
                    - **Technological advancements, trends, or recent developments** in this domain.
                    - **Insights about the company’s work culture, leadership, and market positioning**.
                    
                    **Do NOT include keywords that return job listings or career pages**.
                    
                    ### Job Description:
                    {job_description}
                    
                    Provide ONLY the search term without explanation.
                    """

        # V1
        # prompt = f"""
        # Given the following job description, generate the best search term to find relevant information about this role, 
        # including company projects, industry focus, and related news. The search term should be concise and effective for Google search.
    
        # Job Description:
        # {job_description}
    
        # Provide only the search term without explanation.
        # """
    
        try:
            response=self.openai.chat.completions.create(
                model=self.MODEL,
                messages=[{"role": "system", "content": "You are an expert at creating effective Google search queries."},
                              {"role": "user", "content": prompt}],
            )
            # response = openai.chat.completions.create(
            #     model=MODEL,
            #     messages=[{"role": "system", "content": "You are an expert at creating effective Google search queries."},
            #               {"role": "user", "content": prompt}],
            #     # max_tokens=20
            # )
            return response.choices[0].message.content 
        except Exception as e:
            print(f"Error generating search term: {e}")
            return ""
    
    def google_search(self, search_query, num_results=20):
        """Perform a Google search and get the first `num_results` relevant links (Free method)."""
        links = []
        try:
            
            for url in search(search_query, num_results=num_results):#, stop=num_results, pause=2):
                links.append(url)
        except Exception as e:
            print(f"Error during Google search: {e}")
        
        return links
        
    def get_links_user_prompt(self, website, job_description):
        user_prompt = f"Here is a job description for a position at {website.url}:\n\n{job_description}\n\n"
        user_prompt += "Please determine which pages on the company website are relevant to this job and its context, including job details (job responsibilities, Required Qualifications, preferred requirements, job title), \
                        related projects, teams, departments, research, and company news. Identify all relevant web links and return the full \
                        https URLs in JSON format. Do not include Terms of Service, Privacy Policy, email links, or unrelated pages.\n"
        user_prompt += "Links (some might be relative links):\n"
        user_prompt += "\n".join(website.links)

        return user_prompt


    def get_links(self, url, job_desc):
        website = Website(url)
        # completion: your task is completing this conversation
        response = self.openai.chat.completions.create(
            model=self.MODEL,
            messages=[
                {"role": "system", "content": self.link_system_prompt},
                {"role": "user", "content": self.get_links_user_prompt(website, job_desc)}
          ],
            response_format={"type": "json_object"} # we tell OpenAI, we want Json object back in its response. OpenAI in its documentation recommend that it's still important that you mention in your prompt that a json response is required even if you specify format in this argument.
        )
        result = response.choices[0].message.content 
        # dot choices zero. So what's this about? Well, as it happens we can actually in the API request ask to have multiple variations if we want, 
        # if we wanted it to generate several possible variations of the response. And we haven't done that. So we're only going to get back one.
        # Uh, and so those variations come back in the form of these choices. But we've only got one. So choices zero is getting us the one and the only choice of the response back.
        return json.loads(result)  # we use json.loads to bring it back as JSON.
 
        
    def get_all_details(self, url):
        result = "Landing page:\n"
        result += Website(url).get_contents()
        return result

    def get_brochure_user_prompt(self,company_name, job_desc, url):
        # user_prompt = f"You are looking at a company called: {company_name}\n"
        # user_prompt += f"Here are the contents of its landing page and other relevant pages; use this information to build a short brochure of the company in markdown.\n"
        # user_prompt += self.get_all_details(url)
        user_prompt = f"You are researching a company called: {company_name}.\n\n"
        user_prompt += "Below are the contents of its landing page and other relevant pages. Your goal is to extract and analyze \
                        all information related to a specific job position to help the user understand its full context within the company.\n\n"

        
        # Google Search
        search_term = self.generate_search_term(job_description)
        search_query = f"{search_term} {company_name}"  # Append company name to the search term
    
        print(f"Searching Google for: {search_query}")
        links = self.google_search(search_query, num_results=10)
        print(links)
        for link in links:
            user_prompt += self.get_all_details(link)
            
        user_prompt += "### **Instructions:**\n"
        # user_prompt += "- Identify and extract all details about the job, including responsibilities, qualifications, and benefits.\n"
        user_prompt += "- Find information on the department, team, or projects this job is associated with.\n"
        user_prompt += "- Look for company initiatives, research, or ongoing work that may relate to this role.\n"
        user_prompt += "- Extract any relevant company culture, values, or work environment details that impact this position.\n"
        user_prompt += "- If available, include company news, innovations, or industry focus related to the job role.\n"
        user_prompt += "- Provide a structured and comprehensive response in Markdown format for clarity.\n"
        user_prompt += "- Only show the connections in job descriptions and the webpage content to see what are related things\n"
        user_prompt += "- focus on everything that is related to the job description especially the job title/position title\n"
        # user_prompt += "- if you do not find the related content, just output no information found. Do not generate unnecessary info\n"
        user_prompt += " provide as much information as you can. Also, do not include the job description in the output. Response in markdown format\n"
        user_prompt += "\n### **Job & Company Information:**\n"


        user_prompt = user_prompt[:10_000] # Truncate if more than 10,000 characters, just in case
        return user_prompt


    def create_brochure(self, company_name, url, job_desc):
        response = self.openai.chat.completions.create(
            model=self.MODEL,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": self.get_brochure_user_prompt(company_name, job_desc, url)}
              ],
        )
        result = response.choices[0].message.content
        display(Markdown(result))


SA=SummarizationAgent()
url='https://www.zoetis.com/'
with open('jobDesc.txt','r') as f:
    job_description = f.readlines()
SA.create_brochure('Zoetis',url, job_description)