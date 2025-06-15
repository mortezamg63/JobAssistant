import os
from github import Github
from openai import OpenAI
from dotenv import load_dotenv

class GitHubRepoSummarizer:
    def __init__(self):
        load_dotenv()
        self.access_token = os.getenv("GITHUB_TOKEN")
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.gpt = OpenAI(api_key=self.api_key)
        self.github = Github(self.access_token)
        self.system_prompt = (
            "You are a helpful assistant that summarizes the projects of a GitHub repository. "
            "If you are not able to summarize the code, just return 'No summary available'. "
            "If the content of the file is not README or code related, just return 'No summary available'."
        )
        VIDEO_EXTENSIONS = {'.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mpeg'}
        IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.ico', '.svg'}
        AUDIO_EXTENSIONS = {'.mp3', '.wav', '.ogg', '.flac', '.aac', '.m4a'}
        ARCHIVE_EXTENSIONS = {
            '.zip', '.rar', '.tar', '.gz', '.7z', '.bz2', '.xz',
            '.bin', '.exe', '.dll', '.so', '.o', '.dmg', '.iso'
        }
        self.BINARY_EXTENSIONS = IMAGE_EXTENSIONS | VIDEO_EXTENSIONS | AUDIO_EXTENSIONS | ARCHIVE_EXTENSIONS


    def generate_code_summary(self, code):
        response = self.gpt.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"Summarize this code or text:\n{code[:3000]}"}
            ]
        )
        return response.choices[0].message.content

    def generate_project_summary(self, file_summaries):
        summaries = "\n".join(file_summaries)
        response = self.gpt.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"Here are the file summaries:\n{summaries}"}
            ]
        )
        return response.choices[0].message.content

    def save_repo_report(self, repo_name, content):
        filename = f"{repo_name}_report.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)


    def analyze_github_repositories(self, ACCESS_TOKEN):
        g = Github(ACCESS_TOKEN)
        user = g.get_user()
        
        for repo in user.get_repos():
            
            print(f"Analyzing {repo.full_name}")
            contents = repo.get_contents("")
            file_summaries = []
            # print(f"Contents: {contents}")
            extensions = []
            
            while contents:
                file_content = contents.pop(0)
                if file_content.type == "dir":
                    contents.extend(repo.get_contents(file_content.path))
                else:
                    _, ext = os.path.splitext(file_content.path)
                    print(f"File: {file_content.path}")
                    if (file_content.size < 1000000) and (ext not in self.BINARY_EXTENSIONS):  # Avoid large files
                        try:
                            content = file_content.decoded_content.decode()
                            summary = self.generate_code_summary(content)
                            if summary !='No summary available':
                                file_summaries.append(f"{file_content.path}: {summary}")
                                    
                        except Exception as e:
                            continue
            if len(file_summaries) > 0:
                project_summary = self.generate_project_summary(file_summaries)
                self.save_repo_report(repo.name, project_summary)
                yield {"name": repo.name, "summary": project_summary}


    def analyze_repository(self, repo_full_name):
        try:
            repo = self.github.get_repo(repo_full_name)
        except Exception as e:
            return f"Error accessing repository: {e}"

        contents = repo.get_contents("")
        file_summaries = []

        while contents:
            file_content = contents.pop(0)
            _, ext = os.path.splitext(file_content.path)
            if file_content.type == "dir":
                contents.extend(repo.get_contents(file_content.path))
            elif (file_content.size < 1000000) and (ext not in self.BINARY_EXTENSIONS):
                try:
                    content = file_content.decoded_content.decode()
                    summary = self.generate_code_summary(content)
                    if summary != 'No summary available':
                        file_summaries.append(f"{file_content.path}: {summary}")
                except Exception:
                    continue

        if file_summaries:
            project_summary = self.generate_project_summary(file_summaries)
            self.save_repo_report(repo.name, project_summary)
            return project_summary
        else:
            return "No relevant files found to summarize."

# Example usage (comment out in production if using Flask/HTML UI):
# summarizer = GitHubRepoSummarizer()
# summary = summarizer.analyze_repository("mortezamg63/YOLO-Object-Detecton")
# print(summary)
