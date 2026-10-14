from crewai import Agent, Task

from tools.search_tool import search_web


def create_researcher(llm) -> Agent:
    return Agent(
        role="Web Researcher",
        goal="Find credible, relevant web sources for every research question.",
        backstory="You are an expert online researcher. You only report what the search "
                  "results actually say and you never invent sources or facts.",
        llm=llm,
        tools=[search_web],
        allow_delegation=False,
        max_iter=8,
        verbose=False,
    )


def create_researcher_task(agent: Agent, topic: str, plan_task: Task) -> Task:
    return Task(
        description=(
            f"Research topic: {topic}\n\n"
            "Use the search_web tool for the queries in the research plan "
            "(at most 4 searches in total). For each question, note the facts "
            "found and the exact URL they came from.\n"
            "STRICT RULES: only use information that appears in the search results. "
            "Only use URLs that appear in the search results. If nothing was found "
            "for a question, write 'No evidence found'."
        ),
        expected_output=(
            "Evidence notes grouped by research question. Every fact is followed by "
            "its source URL copied from the search results."
        ),
        agent=agent,
        context=[plan_task],
    )