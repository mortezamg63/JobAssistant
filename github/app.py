from flask import Flask, render_template, request, Response, stream_with_context
from repo_summarizer import GitHubRepoSummarizer
import json
import time

app = Flask(__name__)
app.secret_key = "your-secret-key"
summarizer = GitHubRepoSummarizer()

@app.route("/")
def home():
    return render_template("chat.html")

@app.route("/summarize", methods=["POST"])
def summarize_single_repo():
    repo_url = request.form.get("repo_url", "").strip()
    if repo_url.startswith("https://github.com/"):
        repo_url = repo_url.replace("https://github.com/", "")
    if not repo_url:
        return render_template("chat.html", error="Please enter a valid repository URL.")

    try:
        summary = summarizer.analyze_repository(repo_url)
        return render_template("chat.html", summary=summary)
    except Exception as e:
        return render_template("chat.html", error=f"Error summarizing repository: {str(e)}")



@app.route("/stream-account-summary")
def stream_account_summary():
    access_token = request.args.get("token")
    if not access_token:
        return "Missing access token", 400

    def event_stream():
        for project_summary in summarizer.analyze_github_repositories(access_token):
            # project_summary['name'] += "\n\n-"*len(project_summary['name'])+"\n\n"+project_summary['summary']
            project_summary['name'] = f"{project_summary['name']} -> {project_summary['summary']}"
            print("project summary: ", project_summary['summary'])
            yield f"data: {json.dumps(project_summary)}\n\n"

    return Response(stream_with_context(event_stream()), content_type="text/event-stream")


if __name__ == "__main__":
    app.run(debug=True)




# from flask import Flask, render_template, request
# from repo_summarizer import GitHubRepoSummarizer

# app = Flask(__name__)
# summarizer = GitHubRepoSummarizer()

# @app.route("/")
# def home():
#     return render_template("chat.html")

# @app.route("/summarize", methods=["POST"])
# def summarize_single_repo():
#     repo_url = request.form.get("repo_url", "").strip()
#     repo_url = repo_url.replace("https://github.com/", "") if repo_url.startswith("https://github.com/") else repo_url
#     if repo_url.startswith("https://github.com/"):
#         repo_url = repo_url.replace("https://github.com/", "")
#     if not repo_url:
#         return render_template("chat.html", error="Please enter a valid repository URL.")
    
#     try:
#         summary = summarizer.analyze_repository(repo_url)
#         return render_template("chat.html", summary=summary)
#     except Exception as e:
#         return render_template("chat.html", error=f"Error summarizing repository: {str(e)}")

# @app.route("/account-summary", methods=["POST"])
# def summarize_account_repos():
#     access_token = request.form.get("access_token", "").strip()
#     if not access_token:
#         return render_template("chat.html", account_error="Please provide a GitHub access token.")
    
#     repo_summaries = []
#     try:
#         for project_summary in summarizer.analyze_github_repositories(access_token):
#             repo_summaries.append({
#                 "name": project_summary.split(':')[0].strip(),  # crude title from path
#                 "content": project_summary
#             })
#         return render_template("chat.html", repo_summaries=repo_summaries)
#     except Exception as e:
#         return render_template("chat.html", account_error=f"Error analyzing repositories: {str(e)}")

# if __name__ == "__main__":
#     app.run(debug=True)

