from flask import Flask, render_template, request
# from langchain.prompts import ChatPromptTemplate
# from langchain.chat_models import ChatOpenAI
# from langchain.schema import HumanMessage
from Agent_coverLetter import Agent_coverLetter

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    coverLetter=''
    company_name=''
    company_address=''
    fullname=''
    phone=''
    linkedin=''
    github=''
    job_desc=''
    resume=''
    job_description=''
    if request.method=='POST':
        fullname = request.form['fullname']
        phone = request.form['phone']
        linkedin = request.form['linkedin_link']
        github = request.form['github_link']
        
        job_description = request.form['job_description']
        resume = request.form['resume_text']
    
        coverLetterAgent = Agent_coverLetter(job_description, resume)
    
        company_name, company_address, coverLetter = coverLetterAgent.run()
        # coverLetter += "Sincerely,\n"+fullname
        
    return render_template('index.html', 
                           output=coverLetter,
                           company_name=company_name,
                           company_address = company_address,
                           fullname=fullname,
                            phone=phone,
                            linkedin=linkedin,
                            github=github,
                           job_desc=job_description,
                           resume=resume
                                                 
                          )

if __name__ == '__main__':
    app.run(debug=True)
