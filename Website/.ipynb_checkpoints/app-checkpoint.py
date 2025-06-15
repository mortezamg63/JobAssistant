import os
import json
import datetime
from flask import Flask, render_template, request, redirect, url_for
from profile import profile_bp  # Ensure your profile blueprint is defined in profile.py

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Path for jobs database
JOBS_FILE = "database/jobs.json"
if not os.path.exists(os.path.dirname(JOBS_FILE)):
    os.makedirs(os.path.dirname(JOBS_FILE))

# Register the profile blueprint
app.register_blueprint(profile_bp)

def load_jobs():
    """Load jobs from the JSON file. Returns an empty list if file doesn't exist."""
    if not os.path.exists(JOBS_FILE):
        return []
    with open(JOBS_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_jobs(jobs):
    """Save the jobs list to the JSON file."""
    with open(JOBS_FILE, "w") as f:
        json.dump(jobs, f, indent=4)

@app.route("/", methods=["GET"])
def index():
    """Display active jobs (non-archived) with filtering and sorting."""
    jobs = load_jobs()
    # Exclude archived jobs.
    jobs = [job for job in jobs if job.get("status") != "Archived"]

    filter_status = request.args.get("filter_status")
    sort_key = request.args.get("sort")
    order = request.args.get("order", "asc")

    if filter_status and filter_status != "All":
        jobs = [job for job in jobs if job.get("status") == filter_status]

    allowed_sort_keys = {"title", "company", "location", "status", "date_saved", "last_update"}
    if sort_key in allowed_sort_keys:
        reverse = (order == "desc")
        jobs.sort(key=lambda job: job.get(sort_key, "").lower(), reverse=reverse)

    return render_template("index.html", jobs=jobs)

@app.route("/archived", methods=["GET"])
def archived():
    """Display archived jobs."""
    jobs = load_jobs()
    archived_jobs = [job for job in jobs if job.get("status") == "Archived"]

    filter_status = request.args.get("filter_status")
    sort_key = request.args.get("sort")
    order = request.args.get("order", "asc")

    if filter_status and filter_status != "All":
        archived_jobs = [job for job in archived_jobs if job.get("status") == filter_status]

    allowed_sort_keys = {"title", "company", "location", "status", "date_saved", "last_update"}
    if sort_key in allowed_sort_keys:
        reverse = (order == "desc")
        archived_jobs.sort(key=lambda job: job.get(sort_key, "").lower(), reverse=reverse)

    return render_template("archived.html", jobs=archived_jobs)

@app.route("/job/<int:job_id>")
def job_detail(job_id):
    """Display the detail page for a specific job."""
    jobs = load_jobs()
    job = next((job for job in jobs if job["id"] == job_id), None)
    if not job:
        return redirect(url_for("index"))
    return render_template("detail.html", job=job)

@app.route("/add_job", methods=["POST"])
def add_job():
    """Handle new job submission."""
    jobs = load_jobs()
    new_id = max([job.get("id", 0) for job in jobs], default=0) + 1

    title = request.form.get("title", "").strip()
    original_url = request.form.get("original_url", "").strip()
    company = request.form.get("company", "").strip()
    location = request.form.get("location", "").strip()
    status = request.form.get("status", "Bookmarked").strip()
    description = request.form.get("description", "").strip()
    resume_used = request.form.get("resume_used", "").strip()

    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_job = {
        "id": new_id,
        "title": title,
        "original_url": original_url,
        "company": company,
        "location": location,
        "status": status,
        "description": description,
        "resume_used": resume_used,
        "date_saved": now_str,
        "last_update": now_str
    }

    jobs.append(new_job)
    save_jobs(jobs)

    import pdb; pdb.set_trace()
    # return redirect(url_for("index"))

    # ✅ Check request source: If it's from the extension, return JSON
    if request.headers.get("Accept") == "application/json" or request.headers.get("Content-Type") == "application/json":
        return jsonify({"success": True, "message": "Job added successfully", "job": new_job}), 200

    # ✅ If coming from index.html, redirect to update the job list visually
    return redirect(url_for("index"))

@app.route("/edit_job/<int:job_id>", methods=["GET", "POST"])
def edit_job(job_id):
    """Display and process a form to edit a job."""
    jobs = load_jobs()
    job = next((job for job in jobs if job["id"] == job_id), None)
    if not job:
        return redirect(url_for("index"))
    
    if request.method == "POST":
        job["title"] = request.form.get("title", job["title"]).strip()
        job["original_url"] = request.form.get("original_url", job.get("original_url", "")).strip()
        job["company"] = request.form.get("company", job["company"]).strip()
        job["location"] = request.form.get("location", job["location"]).strip()
        job["status"] = request.form.get("status", job["status"]).strip()
        job["description"] = request.form.get("description", job["description"]).strip()
        job["resume_used"] = request.form.get("resume_used", job.get("resume_used", "")).strip()
        job["last_update"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_jobs(jobs)
        return redirect(url_for("index"))
    
    return render_template("edit_job.html", job=job)

@app.route("/archive_job/<int:job_id>", methods=["POST"])
def archive_job(job_id):
    """Archive a job by setting its status to 'Archived'."""
    jobs = load_jobs()
    for job in jobs:
        if job["id"] == job_id:
            job["status"] = "Archived"
            job["last_update"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            break
    save_jobs(jobs)
    return redirect(url_for("index"))

@app.route("/delete_job/<int:job_id>", methods=["POST"])
def delete_job(job_id):
    """Delete a job from the database."""
    jobs = load_jobs()
    jobs = [job for job in jobs if job["id"] != job_id]
    save_jobs(jobs)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
