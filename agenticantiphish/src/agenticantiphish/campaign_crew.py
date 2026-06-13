from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List


@CrewBase
class CampaignCreationCrew:
    """Phase 1 — generates the campaign strategy brief and phishing email content."""

    agents: List[BaseAgent]
    tasks: List[Task]

    agents_config = "config/campaign_agents.yaml"
    tasks_config = "config/campaign_tasks.yaml"

    @agent
    def campaign_planner(self) -> Agent:
        return Agent(
            #pulls agent's role goal & backstory
            config=self.agents_config["campaign_planner"],  # type: ignore[index]
            verbose=True,
        )

    @agent
    def phishing_email_generator(self) -> Agent:
        return Agent(
            config=self.agents_config["phishing_email_generator"],  # type: ignore[index]
            verbose=True,
        )

    @task
    def plan_campaign_task(self) -> Task:
        return Task(
            config=self.tasks_config["plan_campaign_task"],  # type: ignore[index]
        )

    @task
    def generate_phishing_email_task(self) -> Task:
        return Task(
            config=self.tasks_config["generate_phishing_email_task"],  # type: ignore[index]
            context=[self.plan_campaign_task()],
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
