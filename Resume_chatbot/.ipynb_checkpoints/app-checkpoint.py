from flask import Flask, render_template, request, jsonify


app = Flask(__name__)

# Simple Chatbot logic (replace with your custom logic)
def chatbot_response(user_message):
    # Dummy logic, replace this with your real chatbot logic.
    responses = {
        'hello': 'Hello! How can I assist you today?',
        'how are you': 'I am a bot, but thank you for asking!',
        'bye': 'Goodbye! Have a nice day!',
    }
    return responses.get(user_message.lower(), "Sorry, I don't understand that.")

@app.route("/")
def index():
    return render_template("chat.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    bot_message = chatbot_response(user_message)
    return jsonify({"response": bot_message})

if __name__ == "__main__":
    app.run(debug=True)
