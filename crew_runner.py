"""Builds the crew and runs it, reporting real progress to the UI."""
from crewai import Crew, Process

from agents.analyst import create_analyst, create_analyst_task
from agents.planner import create_planner, create_planner_task
from agents.researcher import create_researcher, create_researcher_task
from agents.writer import create_writer, create_writer_task
from config import build_llm
from tools.search_tool import get_unique_sources, reset_search_log

# Order matters: this is the order the agents run in.
STEPS = ["Research Planner", "Web Researcher", "Research Analyst", "Report Writer"]


def run_research(topic: str, api_key: str, on_status):
    """Run the 4 agents one after another.

    on_status(step_index, status) is called with status in
    {"Working", "Completed", "Failed"} so the UI shows what is REALLY happening.
    Returns a dict: report, findings (analyst notes) and sources (real URLs).
    """
    reset_search_log()
    llm = build_llm(api_key)

    planner, researcher = create_planner(llm), create_researcher(llm)
    analyst, writer = create_analyst(llm), create_writer(llm)

    t1 = create_planner_task(planner, topic)
    t2 = create_researcher_task(researcher, topic, t1)
    t3 = create_analyst_task(analyst, topic, t2)
    t4 = create_writer_task(writer, topic, t3, t2)
    tasks = [t1, t2, t3, t4]

    progress = {"done": 0}

    def when_task_finishes(_output):
        finished = progress["done"]
        on_status(finished, "Completed")
        progress["done"] += 1
        if progress["done"] < len(STEPS):
            on_status(progress["done"], "Working")

    crew = Crew(
        agents=[planner, researcher, analyst, writer],
        tasks=tasks,
        process=Process.sequential,
        task_callback=when_task_finishes,
        verbose=False,
    )

    on_status(0, "Working")
    try:
        result = crew.kickoff()
    except Exception:
        on_status(min(progress["done"], len(STEPS) - 1), "Failed")
        raise

    return {
        "report": str(result.raw),
        "findings": str(tasks[2].output.raw) if tasks[2].output else "",
        "sources": get_unique_sources(),
    }