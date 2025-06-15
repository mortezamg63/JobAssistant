import asyncio
import json
from pathlib import Path
from flask import Flask, render_template, request, jsonify, Response
from agents import Agent, Runner
from models import ResumeMatchOutput

app = Flask(__name__, template_folder="templates", static_folder="static")

# Load prompts
system_prompt = Path("prompts/system.txt").read_text()
user_template = Path("prompts/user.txt").read_text()

# Instantiate the Agent
resumeMatch_Agent = Agent(
    name="ResumeOptimizer",
    instructions=system_prompt,
    model="gpt-4o-mini",
    output_type=ResumeMatchOutput
)

@app.route("/")
def index():
    return render_template("resumeBuilder.html")

@app.route("/api/suggestions", methods=["POST"])
def suggestions():
    payload = request.get_json()
    file = open('resume.txt')
    resume_json    = file.readlines() #payload["resume"]
    job_description = payload["job_description"]

    # Fill in the user prompt
    user_prompt = user_template.format(
        resume=json.dumps(resume_json, indent=2),
        job_description=job_description
    )

 
    runner = Runner()#, user_prompt)
    import pdb; pdb.set_trace()
    output: ResumeMatchOutput = asyncio.run(runner.run(resumeMatch_Agent,user_prompt))
    print(output)
    # return jsonify(output.dict())
    # app.logger.debug("Agent output (dict): %s", output.model_dump())

    # 4) return raw JSON
    
    json_text = output.model_dump_json()   # JSON string from Pydantic
    return Response(json_text, status=200, mimetype="application/json")

if __name__ == "__main__":
    app.run(debug=True)
