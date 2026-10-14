

from crewai import Agent, Task

from tools.search_tool import search_web
from tools.web_reader import open_file


def create_researcher(llm) -> Agent:
    return Agent(
        role="Web Researcher",
        goal="Find reliable web sources and examine relevant evidence.",
        backstory=(
            "You are a careful web researcher. First use search_web "
            "to discover sources. You may then use open_file with "
            "the exact HTTPS URL returned by search_web to read a "
            "relevant page or PDF. Use only registered tools and "
            "never invent tool names, URLs, or facts."
        ),
        llm=llm,
        tools=[search_web, open_file],
        allow_delegation=False,
        max_iter=8,
        verbose=True,
    )



def create_researcher_task(
    agent: Agent, topic: str, plan_task: Task
) -> Task:
    return Task(
        description=(
            f"Research topic: {topic}\n\n"
            "Read the research plan supplied in the context. "
            "Use search_web for up to four distinct queries. "
            "Each query must be passed as the tool's 'query' argument. "
            "Do not attempt to open files or webpages using other tools. "
            "Use only titles, URLs and snippets returned by search_web.\n\n"
            "For each research question, provide the available facts, "
            "the exact source URLs returned by search_web, and any "
            "evidence gaps. If no evidence is found, say so."
        ),
        expected_output=(
            "Evidence notes grouped by research question, with "
            "source URLs copied from search results."
        ),
        agent=agent,
        context=[plan_task],
    )
