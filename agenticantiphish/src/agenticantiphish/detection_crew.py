from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List

from agenticantiphish.tools import SplunkMCPTool


@CrewBase
class DetectionCrew:
    """Phase 3 — queries Splunk via MCP to find employees who clicked phishing links."""

    agents: List[BaseAgent]
    tasks: List[Task]

    agents_config = "config/detection_agents.yaml"
    tasks_config = "config/detection_tasks.yaml"

    @agent
    def splunk_monitor(self) -> Agent:
        return Agent(
            config=self.agents_config["splunk_monitor"],  # type: ignore[index]
            tools=[SplunkMCPTool()],
            verbose=True,
        )

    @task
    def detect_clicks_task(self) -> Task:
        return Task(
            config=self.tasks_config["detect_clicks_task"],  # type: ignore[index]
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
