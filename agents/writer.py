from crewai import Agent, Task


def create_writer(llm) -> Agent:
    return Agent(
        role="Report Writer",
        goal="Write a clear, well-structured research report based only on the analysis.",
        backstory="You are a professional writer. You explain things in plain language "
                  "and always cite the source URL for factual claims.",
        llm=llm,
        tools=[],
        allow_delegation=False,
        verbose=False,
    )


def create_writer_task(agent: Agent, topic: str, analysis_task: Task, research_task: Task) -> Task:
    return Task(
        description=(
            f"Research topic: {topic}\n\n"
            "Write the final report in Markdown using these sections:\n"
            "# <Title>\n## Executive Summary\n## Key Findings\n## Detailed Analysis\n"
            "## Limitations\n## Conclusion\n\n"
            "Rules: use only the analysis and evidence provided, cite source URLs next "
            "to claims, and be honest about limitations. Do not add a sources list "
            "(the app adds it)."
        ),
        expected_output="A complete Markdown research report.",
        agent=agent,
        context=[analysis_task, research_task],
    )