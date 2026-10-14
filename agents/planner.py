from crewai import Agent, Task


def create_planner(llm) -> Agent:
    return Agent(
        role="Research Planner",
        goal="Turn a research topic into clear research questions and search queries.",
        backstory="You are a careful research lead. You break big topics into small, "
                  "answerable questions and decide what evidence is needed.",
        llm=llm,
        tools=[],
        allow_delegation=False,
        verbose=False,
    )


def create_planner_task(agent: Agent, topic: str) -> Task:
    return Task(
        description=(
            f"Research topic: {topic}\n\n"
            "Create a short research plan:\n"
            "1. Write 4 specific research questions.\n"
            "2. For each question, write 1 web search query.\n"
            "Keep it brief. Do not answer the questions."
        ),
        expected_output="A numbered list of 4 research questions, each with one search query.",
        agent=agent,
    )