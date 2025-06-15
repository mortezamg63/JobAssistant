from openai import OpenAI
import os
from dotenv import load_dotenv
import gradio as gr
import os

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
openai = OpenAI(api_key=api_key)


# reading all reports and resume
directory = 'reports'
txt_files = [f for f in os.listdir(directory) if f.endswith('.txt')]

content = []
for txt_file in txt_files:
    with open(os.path.join(directory, txt_file), 'r') as file:
        file_content = txt_file.split('.')[0].replace('_',' ')+"\n------------------"+file.read()
        content.append(file_content)


system_prompt = "You are a resume chatbot whose name is Mory Gharasuie. You are given a resume and you need to answer the questions based on the resume. \n\n"
system_prompt += "Resume: \n\n"
system_prompt += "\n".join(content)
system_prompt += "\n you get the user question and you need to answer the question based on the resume. \n\n"
system_prompt += "\n\n to answer the question, you extract the keywords from the resume and user questions and then answer the question based on the keywords. make sure you do not miss any information from the resume related to the user question. \n\n"


user_prompt = ""

def chat(message,history):
    messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": message}]
    response = openai.chat.completions.create(model="gpt-4o-mini", messages=messages)
    return response.choices[0].message.content