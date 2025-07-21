from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List

# from crewai.config import ConfigLoader

# config_loader = ConfigLoader(agent_path="agents.yaml", task_path="tasks.yaml")

# agents_config: dict[str, AgentConfig] = config_loader.load_agents()
# tasks_config: dict[str, TaskConfig] = config_loader.load_tasks_dict()  # ✅ Fix is here


# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class LinkedinProposal():
    """LinkedinProposal crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def linkedin_profile_coach(self) -> Agent:
        output= Agent(
            config=self.agents_config['linkedin_profile_coach'], # type: ignore[index]
            verbose=True
        )
        # print("coach agent output: ", output)
        return output

    @agent
    def profile_schema_validator(self) -> Agent:
        return Agent(
            config=self.agents_config['profile_schema_validator'], # type: ignore[index]
            verbose=True
        )

    @task
    def generate_linkedin_profile_task(self) -> Task:
        # import pdb; pdb.set_trace()
        return Task(
            config=self.tasks_config['generate_linkedin_profile_task'], # type: ignore[index]
        )

    @task
    def validate_profile_schema_task(self) -> Task:
        return Task(
            config=self.tasks_config['validate_profile_schema_task'], # type: ignore[index]
        )
        
    # @agent
    # def linkedin_profile_validator(self) -> Agent:
    #     return Agent(
    #         config=self.agents_config['linkedin_profile_validator'], # type: ignore[index]
    #         verbose=True
    #     )
    
    # @agent
    # def finalize_profile_workflow_task(self) -> Agent:
    #     return Agent(
    #         config=self.agents_config['finalize_profile_workflow_task'], # type: ignore[index]
    #         verbose=True
    #     )
    # # To learn more about structured task outputs,
    # # task dependencies, and task callbacks, check out the documentation:
    # # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    # @task
    # def analyze_resume_json_task(self) -> Task:
    #     return Task(
    #         config=self.tasks_config['analyze_resume_json_task'], # type: ignore[index]
    #     )

    # @task
    # def draft_linkedin_profile_task(self) -> Task:
    #     return Task(
    #         config=self.tasks_config['draft_linkedin_profile_task'], # type: ignore[index]
    #         # output_file='report.md'
    #     )

    # @task
    # def executive_profile_feedback_task(self) -> Task:
    #     return Task(
    #         config=self.tasks_config['executive_profile_feedback_task'], # type: ignore[index]
    #         # output_file='report.md'
    #     )

    # @task
    # def revise_profile_with_feedback_task(self) -> Task:
    #     return Task(
    #         config=self.tasks_config['revise_profile_with_feedback_task'], # type: ignore[index]
    #         # output_file='report.md'
    #     )

    # @task
    # def validate_profile_completeness_task(self) -> Task:
    #     return Task(
    #         config=self.tasks_config['validate_profile_completeness_task'], # type: ignore[index]
    #         # output_file='report.md'
    #     )

    # @task
    # def review_role_alignment_task(self) -> Task:
    #     return Task(
    #         config=self.tasks_config['review_role_alignment_task'], # type: ignore[index]
    #         # output_file='report.md'
    #     )

    # @task
    # def suggest_profile_improvements_task(self) -> Task:
    #     return Task(
    #         config=self.tasks_config['suggest_profile_improvements_task'], # type: ignore[index]
    #         # output_file='report.md'
    #     )

    # @task
    # def finalize_validation_task(self) -> Task:
    #     return Task(
    #         config=self.tasks_config['finalize_validation_task'], # type: ignore[index]
    #         # output_file='report.md'
    #     )

    # @task
    # def orchestrate_profile_creation_task(self) -> Task:
    #     return Task(
    #         config=self.tasks_config['orchestrate_profile_creation_task'], # type: ignore[index]
    #         # output_file='report.md'
    #     )

    # @task
    # def handle_revision_cycle_task(self) -> Task:
    #     return Task(
    #         config=self.tasks_config['handle_revision_cycle_task'], # type: ignore[index]
    #         # output_file='report.md'
    #     )

    # @task
    # def finalize_profile_workflow_task(self) -> Task:
    #     return Task(
    #         config=self.tasks_config['finalize_profile_workflow_task'], # type: ignore[index]
    #         output_file='final_profile.md'
    #    )
    

    @crew
    def crew(self) -> Crew:
        """Creates the LinkedinProposal crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
