from flask import Flask, render_template, request
from repo_summarizer import GitHubRepoSummarizer

app = Flask(__name__)
summarizer = GitHubRepoSummarizer()

@app.route("/")
def home():
    return render_template("summarizer_github.html")

@app.route("/summarize", methods=["POST"])
def summarize():
    repo_url = request.form.get("repo_url")
    if not repo_url:
        return render_template("summarizer_github.html", error="Please enter a valid repository URL.")

    try:
        summary = summarizer.analyze_repository(repo_url)
        return render_template("summarizer_github.html", summary=summary)
    except Exception as e:
        return render_template("summarizer_github.html", error=f"An error occurred: {str(e)}")

if __name__ == "__main__":
    app.run(debug=True)
