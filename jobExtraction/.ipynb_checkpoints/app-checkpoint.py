import subprocess
from flask import Flask, render_template, request, redirect, url_for
import yaml
import pandas as pd

app = Flask(__name__)

# Path to your YAML configuration and CSV file
YAML_FILE_PATH = 'my_settings.yaml'
CSV_FILE_PATH = 'job_search_results/demo_search.csv'


def load_yaml():
    with open(YAML_FILE_PATH, 'r') as file:
        return yaml.safe_load(file)


def save_yaml(data):
    with open(YAML_FILE_PATH, 'w') as file:
        yaml.dump(data, file)


def load_csv():
    return pd.read_csv(CSV_FILE_PATH)


@app.route('/')
def index():
    config = load_yaml()
    return render_template('index.html', config=config)

def run_funnel_load_command():
    try:
        # This command assumes you have "funnel" installed and available in your system PATH
        subprocess.run(["funnel", "load", "-s", "my_settings.yaml"], check=True)
        print("Command executed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        return False
    return True

@app.route('/update_config', methods=['POST'])
def update_config():
    config = load_yaml()

    # Update the fields in the YAML with user input
    config['search']['locale'] = request.form['locale']
    config['search']['providers'] = request.form.getlist('providers')
    config['search']['province_or_state'] = request.form['province_or_state']
    config['search']['city'] = request.form['city']
    config['search']['radius'] = int(request.form['radius'])
    config['search']['keywords'] = request.form.getlist('keywords')
    config['search']['max_listing_days'] = int(request.form['max_listing_days'])
    config['search']['company_block_list'] = request.form.getlist('company_block_list')
    config['search']['remoteness'] = request.form['remoteness']

    save_yaml(config)

    if run_funnel_load_command():
        return redirect(url_for('show_jobs'))
    else:
        return "Error executing the command", 500  # If the command fails, show an error message
    
    return render_template('index.html', config=load_yaml_config(), success=False)


# @app.route('/show_jobs')
# def show_jobs():
#     jobs_df = load_csv()
#     # return render_template('show_jobs.html', jobs=jobs_df.to_html(classes='table table-striped'))
#     jobs = jobs_df.to_dict(orient='records')
    
#     # Pass jobs to the template
#     return render_template('show_jobs.html', jobs=jobs)

@app.route('/show_jobs')
def show_jobs():
    jobs_df = load_csv()

    # Convert DataFrame to list of dictionaries
    jobs = jobs_df.to_dict(orient='records')

    # Get the search query from the request
    search_query = request.args.get('search', '').strip().lower()

    # Filter jobs if a search query is provided
    if search_query:
        jobs = [job for job in jobs if any(search_query in str(value).lower() for value in job.values())]

    return render_template('show_jobs.html', jobs=jobs, search_query=search_query)


if __name__ == '__main__':
    app.run(debug=True)



# import os
# from flask import Flask, render_template, request, jsonify
# import pandas as pd
# import yaml

# app = Flask(__name__)

# # Load the YAML file
# def load_yaml_config():
#     with open("my_settings.yaml", 'r') as file:
#         config = yaml.safe_load(file)
#     return config

# # Save the updated YAML config
# def save_yaml_config(config):
#     with open("my_settings.yaml", 'w') as file:
#         yaml.dump(config, file)

# # Load job search results CSV
# def load_job_csv():
#     csv_file = "job_search_results/demo_search.csv"
#     if os.path.exists(csv_file):
#         return pd.read_csv(csv_file)
#     return pd.DataFrame()

# # Default job search configuration
# default_config = load_yaml_config()

# @app.route("/", methods=["GET", "POST"])
# def index():
#     if request.method == "POST":
#         # Capture the form data and update the YAML config
#         updated_config = default_config.copy()
#         updated_config['search']['locale'] = request.form['locale']
#         updated_config['search']['remoteness'] = request.form['remoteness']
#         updated_config['search']['company_block_list'] = request.form.getlist('company_block_list')
        
#         # Save updated config to YAML
#         save_yaml_config(updated_config)
#         return render_template('index.html', config=updated_config, success=True)

#     return render_template('index.html', config=default_config, success=False)


# @app.route("/jobs", methods=["GET"])
# def jobs():
#     # Load job search results CSV
#     job_df = load_job_csv()
    
#     # Convert job data to dictionary for display
#     job_data = job_df.to_dict(orient="records")
#     return render_template('jobs.html', job_data=job_data)

# if __name__ == "__main__":
#     app.run(debug=True)

