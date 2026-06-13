from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List

from agenticantiphish.tools import EmailSendTool


@CrewBase
class EmailDispatchCrew:
    """Phase 2 — sends phishing simulation emails and logs dispatch events to Splunk."""

    agents: List[BaseAgent]
    tasks: List[Task]

    agents_config = "config/dispatch_agents.yaml"
    tasks_config = "config/dispatch_tasks.yaml"

    @agent
    def email_dispatcher(self) -> Agent:
        return Agent(
            config=self.agents_config["email_dispatcher"],  # type: ignore[index]
            tools=[EmailSendTool()],
            verbose=True,
        )

    @task
    def dispatch_emails_task(self) -> Task:
        return Task(
            config=self.tasks_config["dispatch_emails_task"],  # type: ignore[index]
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
