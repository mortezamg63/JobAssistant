#!/usr/bin/env python
# src/financial_researcher/main.py
import os
from financial_researcher.crew import ResearchCrew

# Create output directory if it doesn't exist
os.makedirs('output', exist_ok=True)
job_description="""
About the Job
Waymo interns work alongside leaders in the industry on projects that deliver significant impact to the company. We believe learning is a two-way street: leveraging your knowledge while providing you with opportunities to expand your skill-set. Interns are an important part of our culture and our recruiting pipeline. Join us at Waymo for a fun and rewarding internship!
Job Responsibilities
Design and develop deep learning models, including Vision Language Models (VLMs) and Large Language Models (LLMs), on real-world sensor data (cameras, LiDAR, radars)
Explore leveraging VLM’s world knowledge and reasoning capabilities to improve various driving tasks
Collaborate and work in partnership with research teams across Alphabet
Requirements
Pursuing a Masters or PhD program in Computer Science, Electrical Engineering, Machine Learning, or related technical fields
Experience with Deep Learning, VLM/LLMs, and/or Computer Vision
Experience with Python and deep learning frameworks such as Jax, Tensorflow, Pytorch
"""
def run():
    """
    Run the research crew.
    """
    inputs = {
        'company': 'Waymo',
        'job_description': job_description
    }

    # Create and run the crew
    result = ResearchCrew().crew().kickoff(inputs=inputs)

    # Print the result
    print("\n\n=== FINAL REPORT ===\n\n")
    print(result.raw)

    print("\n\nReport has been saved to output/report.md")

if __name__ == "__main__":
    run()