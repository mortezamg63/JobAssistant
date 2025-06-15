from flask import Flask, render_template, request, jsonify, session

from openai import OpenAI
import os
from dotenv import load_dotenv
import os
import chatWithResume


app = Flask(__name__)
import secrets
app.secret_key = secrets.token_hex(32)  # generates a secure 64-char key





load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
openai = OpenAI(api_key=api_key)

resume_chat = chatWithResume.ResumeChat('reports', openai)

# # Simple Chatbot logic (replace with your custom logic)
# def chatbot_response(user_message):
#     # Dummy logic, replace this with your real chatbot logic.
#     responses = {
#         'hello': 'Hello! How can I assist you today?',
#         'how are you': 'I am a bot, but thank you for asking!',
#         'bye': 'Goodbye! Have a nice day!',
#     }
#     return responses.get(user_message.lower(), "Sorry, I don't understand that.")

@app.route("/")
def index():
        # Reset history if needed
        if "history" not in session:
            session["history"] = []
        return render_template("chat.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    # Initialize chat history if it doesn't exist
    if "history" not in session:
        session["history"] = []

    history = session["history"]
    bot_message = resume_chat.chat(user_message, history) #chatbot_response(user_message)
    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": bot_message})
    session["history"] = history
    return jsonify({"response": bot_message})

if __name__ == "__main__":
    app.run(debug=True)
