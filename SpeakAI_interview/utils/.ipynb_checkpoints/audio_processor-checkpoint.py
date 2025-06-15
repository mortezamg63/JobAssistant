from openai import OpenAI
import pyttsx3
import os
import json
from dotenv import load_dotenv
import whisper
# Initialization
from pydub import AudioSegment
import os
import subprocess
from io import BytesIO
import tempfile
from pydub.playback import play
from gtts import gTTS


class AudioProcessor:
    def __init__(self):
        load_dotenv()

        openai_api_key = os.getenv('OPENAI_API_KEY')
        if openai_api_key:
            print(f"OpenAI API Key exists and begins {openai_api_key[:8]}")
        else:
            print("OpenAI API Key not set")
            
        self.MODEL = "gpt-4o-mini"
        self.openai = OpenAI()
        self.whisper_model = whisper.load_model("base")

        # Global variable to store chat history
        self.conversation = []
        self.chat_history = []
        self.system_prompt = """
            You are an intelligent and professional AI interviewer. Your task is to conduct a full, structured, and adaptive job interview based on the candidate’s resume and the job description provided.
            
            Your behavior must simulate a real interviewer who is knowledgeable, conversational, and focused on understanding the candidate's suitability for the job.
            
            ---
            
            🔹 Step 1: Analyze the Resume and Job Description
            
            - Carefully read and analyze the **resume** and the **job description**.
            - Identify the following from the resume:
              - Education background
              - Work experience
              - Technical and soft skills
              - Certifications, publications, and projects
              - Industry or research focus
            - Identify the following from the job description:
              - Required technical and soft skills
              - Key responsibilities
              - Preferred qualifications and experiences
              - Domain-specific tools, technologies, or methods
            
            ---
            
            🔹 Step 2: Identify Skill Gaps
            
            - Compare the resume to the job description.
            - If certain important requirements from the job description are not present in the resume, prepare targeted questions to ask the candidate about them.
            - Do **not fabricate** questions: if a skill, tool, or responsibility is **not mentioned** in **either the resume or the job description**, **you may skip that line of questioning**.
            
            ---
            
            🔹 Step 3: Interview Structure and Flow
            
            Organize the interview into the following **five categories**, in this specific order:
            
            1. Technical Skills and Domain Knowledge (Start here)
            2. Problem Solving and Critical Thinking
            3. Background and Motivation
            4. Behavioral and Communication Skills
            5. Career Goals and Cultural Fit
            
            For each category:
            - Generate 4–6 relevant and open-ended questions.
            - Use the resume and job description to customize each question.
            - Simulate a real back-and-forth: ask one question, wait for the user (candidate) to respond, then move to the next question.
            - If a job requirement is missing or unclear in the resume, ask the candidate to elaborate or explain.
            - After finishing a category, clearly inform the candidate that you're moving to the next section.
            
            ---
            
            🔹 Step 4: Ending the Interview
            
            Once you have asked appropriate questions from all categories:
            - Thank the candidate for their time.
            - Optionally summarize the candidate’s key strengths and any follow-ups.
            - End the interview clearly and professionally.
            
            ---
            
            🧠 Guidelines:
            
            - Be friendly, professional, and structured.
            - Prioritize questions grounded in resume and job description.
            - Avoid repetition or unrelated questions.
            - Ask clarifying questions when resume is vague or incomplete.
            - Do **not** fabricate content. Skip any question if it's not supported by the given context.
            
            You must now begin the interview by saying:
            “Let’s begin the interview with Technical Skills and Domain Knowledge...”
            
            Wait for the candidate’s response after each question.
            """
        self.user_prompt = """
                        ### Job Description:
                        {job_description}
                        
                        ### Candidate Resume:
                        {resume_text}

                        please go ahead and start the interview with a short greeting
                        """

        self.user_prompt_resume = "Here is the candidate's resume:\n"
        self.resume_text = None
        self.conversation.append({"role": "system", "content": self.system_prompt})

    def set_resume_and_jobdescript(self, resume_content, job_content):
        self.conversation.append({"role": "user", "content": self.user_prompt.format(job_description=job_content, resume_text=resume_content)})
        


    def transcribe_audio(self, audio_path):    
        # print("Transcribing audio...")
        result = whisper_model.transcribe(audio_path, language="en")
        return result["text"]

    
    def talker(self, message):
        # Mocked OpenAI response for testing
        # import pdb; pdb.set_trace()
        response = self.openai.audio.speech.create(
            model="tts-1",
            voice="onyx",
            input=message
        )
        
        # Handle audio stream
        audio_stream = BytesIO(response.content)
        audio = AudioSegment.from_file(audio_stream, format="mp3")
        
        # Play the audio
        # play_audio_with_ffplay(audio, custom_temp_dir)
        play(audio)
        return audio

    # Function to transcribe audio and update chat history
    def update_chat(self,audio_path):
        # global conversation, chat_history
        # import pdb; pdb.set_trace()
        # Step 1: Transcribe audio
        with open(audio_path, "rb") as audio_file:
            transcription = self.openai.audio.transcriptions.create(model="whisper-1", file = audio_file)
        user_input = transcription.text#["text"]
    
        # Add user input to conversation and chat history
        self.conversation.append({"role": "user", "content": user_input})
        self.chat_history.append(("User", user_input))
    
        # Step 2: Generate response using ChatGPT
        response = self.openai.chat.completions.create(
            model=self.MODEL,#"gpt-3.5-turbo",
            messages=self.conversation
        )
        assistant_response = response.choices[0].message.content
    
        # Add assistant response to conversation and chat history
        self.conversation.append({"role": "assistant", "content": assistant_response})
        self.chat_history.append(("Bot", assistant_response))
        # import pdb; pdb.set_trace()
        out_audio = self.talker(assistant_response)
        # Return updated chat history (audio will be added later)
        return self.chat_history, out_audio  # No audio at this step


    # Function to generate audio for the latest bot response
    def generate_audio(self):
        # global chat_history
        # import pdb; pdb.set_trace()
    
        # Get the last bot response
        if self.chat_history:
            last_bot_response = self.chat_history[-1][1]
        else:
            last_bot_response = "No response available."
    
        # Generate TTS for the bot response
        tts = gTTS(last_bot_response)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(temp_file.name)
        self.talker(last_bot_response)
    
        # Return the audio file path
        # return temp_file.name
