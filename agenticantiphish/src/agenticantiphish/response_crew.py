from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List

from agenticantiphish.tools import EmailSendTool, SplunkHECTool


@CrewBase
class ResponseCrew:
    """Phase 4 — generates personalised threat explanation + training, sends remediation email."""

    agents: List[BaseAgent]
    tasks: List[Task]

    agents_config = "config/response_agents.yaml"
    tasks_config = "config/response_tasks.yaml"

    @agent
    def threat_explainer(self) -> Agent:
        return Agent(
            config=self.agents_config["threat_explainer"],  # type: ignore[index]
            verbose=True,
        )

    @agent
    def training_content_generator(self) -> Agent:
        return Agent(
            config=self.agents_config["training_content_generator"],  # type: ignore[index]
            verbose=True,
        )

    @agent
    def response_sender(self) -> Agent:
        return Agent(
            config=self.agents_config["response_sender"],  # type: ignore[index]
            tools=[EmailSendTool(), SplunkHECTool()],
            verbose=True,
        )

    @task
    def explain_threat_task(self) -> Task:
        return Task(
            config=self.tasks_config["explain_threat_task"],  # type: ignore[index]
        )

    @task
    def generate_training_task(self) -> Task:
        return Task(
            config=self.tasks_config["generate_training_task"],  # type: ignore[index]
        )

    @task
    def send_response_task(self) -> Task:
        return Task(
            config=self.tasks_config["send_response_task"],  # type: ignore[index]
            context=[self.explain_threat_task(), self.generate_training_task()],
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
