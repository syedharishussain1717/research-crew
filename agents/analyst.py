from crewai import Agent, Task


def create_analyst(llm) -> Agent:
    return Agent(
        role="Research Analyst",
        goal="Find the most important insights, patterns and gaps in the collected evidence.",
        backstory="You are a sharp analyst. You compare sources, spot agreement and "
                  "disagreement, and clearly state when evidence is weak or missing.",
        llm=llm,
        tools=[],
        allow_delegation=False,
        verbose=False,
    )


def create_analyst_task(agent: Agent, topic: str, research_task: Task) -> Task:
    return Task(
        description=(
            f"Research topic: {topic}\n\n"
            "Using ONLY the evidence notes from the Web Researcher:\n"
            "1. List 5 key findings, each with its supporting source URL.\n"
            "2. Note any disagreements between sources.\n"
            "3. Note gaps: what could not be confirmed.\n"
            "Do not add facts that are not in the evidence."
        ),
        expected_output="Key findings (with URLs), disagreements, and evidence gaps.",
        agent=agent,
        context=[research_task],
    )