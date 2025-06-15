import os
import json
import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash

profile_bp = Blueprint('profile', __name__, template_folder='templates')

PROFILE_FILE = "database/profile.json"
UPLOAD_FOLDER = "uploads"

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def load_profile():
    """Load profile data from the JSON file."""
    if not os.path.exists(PROFILE_FILE):
        return {}
    with open(PROFILE_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_profile(data):
    """Save the profile data to the JSON file."""
    with open(PROFILE_FILE, "w") as f:
        json.dump(data, f, indent=4)

@profile_bp.route("/profile", methods=["GET", "POST"])
def profile():
    if request.method == "POST":
        # Load existing data so that dynamic arrays are preserved.
        profile_data = load_profile()
        profile_data["first_name"] = request.form.get("first_name", "").strip()
        profile_data["middle_name"] = request.form.get("middle_name", "").strip()
        profile_data["last_name"] = request.form.get("last_name", "").strip()
        profile_data["email"] = request.form.get("email", "").strip()
        profile_data["phone"] = request.form.get("phone", "").strip()
        profile_data["address"] = request.form.get("address", "").strip()
        profile_data["birth_date"] = request.form.get("birth_date", "").strip()
        
        # Basic arrays (projects, social URLs, skills, languages) are updated here:
        profile_data["projects"] = request.form.getlist("projects[]")
        profile_data["social_urls"] = request.form.getlist("social_urls[]")
        profile_data["skills"] = request.form.get("skills", "").strip()
        profile_data["languages"] = request.form.get("languages", "").strip()
        
        # Preserve dynamic arrays if they already exist.
        if "work_experiences" not in profile_data:
            profile_data["work_experiences"] = []
        if "academic_experiences" not in profile_data:
            profile_data["academic_experiences"] = []
        if "educations" not in profile_data:
            profile_data["educations"] = []
        if "publications" not in profile_data:
            profile_data["publications"] = []
        if "projects" not in profile_data:
            profile_data["projects"] = []
        
        # Handle file uploads
        if "profile_pic" in request.files:
            file = request.files["profile_pic"]
            if file and file.filename:
                filename = "profile_pic_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S_") + file.filename
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                profile_data["profile_pic"] = filename
        if "resume_file" in request.files:
            file = request.files["resume_file"]
            if file and file.filename:
                filename = "resume_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S_") + file.filename
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                profile_data["resume_file"] = filename

        profile_data["last_update"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_profile(profile_data)
        flash("Profile updated successfully!")
        return redirect(url_for("profile.profile"))
    else:
        data = load_profile()
        return render_template("profile.html", profile=data)

@profile_bp.route("/profile/add_work_experience", methods=["POST"])
def add_work_experience():
    profile_data = load_profile()
    if "work_experiences" not in profile_data:
        profile_data["work_experiences"] = []
    
    new_experience = {
        "company": request.form.get("company", "").strip(),
        "location": request.form.get("location", "").strip(),
        "position_title": request.form.get("position_title", "").strip(),
        "experience_type": request.form.get("experience_type", "").strip(),
        "start_month": request.form.get("start_month", "").strip(),
        "start_year": request.form.get("start_year", "").strip(),
        "end_month": request.form.get("end_month", "").strip(),
        "end_year": request.form.get("end_year", "").strip(),
        "currently_work_here": request.form.get("currently_work_here") == "on",
        "description": request.form.get("description", "").strip()
    }
    
    profile_data["work_experiences"].append(new_experience)
    profile_data["last_update"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_profile(profile_data)
    flash("Work experience added!")
    return redirect(url_for("profile.profile"))

@profile_bp.route("/profile/add_academic_experience", methods=["POST"])
def add_academic_experience():
    profile_data = load_profile()
    if "academic_experiences" not in profile_data:
        profile_data["academic_experiences"] = []
    
    new_academic = {
        "company": request.form.get("company", "").strip(),
        "location": request.form.get("location", "").strip(),
        "position_title": request.form.get("position_title", "").strip(),
        "experience_type": request.form.get("experience_type", "").strip(),
        "start_month": request.form.get("start_month", "").strip(),
        "start_year": request.form.get("start_year", "").strip(),
        "end_month": request.form.get("end_month", "").strip(),
        "end_year": request.form.get("end_year", "").strip(),
        "currently_work_here": request.form.get("currently_work_here") == "on",
        "description": request.form.get("description", "").strip()
    }
    
    profile_data["academic_experiences"].append(new_academic)
    profile_data["last_update"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_profile(profile_data)
    flash("Academic experience added!")
    return redirect(url_for("profile.profile"))

@profile_bp.route("/profile/add_education", methods=["POST"])
def add_education():
    profile_data = load_profile()
    if "educations" not in profile_data:
        profile_data["educations"] = []
    
    new_edu = {
        "school_name": request.form.get("school_name", "").strip(),
        "new_school_name": request.form.get("new_school_name", "").strip(),
        "major": request.form.get("major", "").strip(),
        "degree_type": request.form.get("degree_type", "").strip(),
        "gpa": request.form.get("gpa", "").strip(),
        "start_month": request.form.get("start_month", "").strip(),
        "start_year": request.form.get("start_year", "").strip(),
        "end_month": request.form.get("end_month", "").strip(),
        "end_year": request.form.get("end_year", "").strip()
    }
    
    profile_data["educations"].append(new_edu)
    profile_data["last_update"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_profile(profile_data)
    flash("Education added!")
    return redirect(url_for("profile.profile"))

@profile_bp.route("/profile/add_publication", methods=["POST"])
def add_publication():
    profile_data = load_profile()
    if "publications" not in profile_data:
        profile_data["publications"] = []
    
    new_pub = {
        "title": request.form.get("title", "").strip(),
        "authors": request.form.get("authors", "").strip(),
        "link": request.form.get("link", "").strip(),
        "year": request.form.get("year", "").strip(),
        "publisher": request.form.get("publisher", "").strip()
    }
    
    profile_data["publications"].append(new_pub)
    profile_data["last_update"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_profile(profile_data)
    flash("Publication added!")
    return redirect(url_for("profile.profile"))

@profile_bp.route("/profile/add_project", methods=["POST"])
def add_project():
    profile_data = load_profile()
    if "projects" not in profile_data:
        profile_data["projects"] = []
    new_project = {
        "title": request.form.get("project_title", "").strip(),
        "description": request.form.get("project_description", "").strip(),
        "link": request.form.get("project_link", "").strip()
    }
    profile_data["projects"].append(new_project)
    profile_data["last_update"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_profile(profile_data)
    flash("Project added!")
    return redirect(url_for("profile.profile"))

@profile_bp.route("/profile/add_social_link", methods=["POST"])
def add_social_link():
    profile_data = load_profile()
    if "social_urls" not in profile_data:
        profile_data["social_urls"] = []
    new_link = request.form.get("social_url", "").strip()
    if new_link:
        profile_data["social_urls"].append(new_link)
        profile_data["last_update"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_profile(profile_data)
        flash("Social link added!")
    return redirect(url_for("profile.profile"))
