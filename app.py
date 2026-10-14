"""Research Multi-Agent System - Streamlit app (run this file on Streamlit Cloud)."""
import streamlit as st

from config import MODEL_NAME, get_api_key
from crew_runner import STEPS, run_research

st.set_page_config(page_title="AI Research Team", page_icon="🔎", layout="wide")

# ---------- Styling ----------
st.markdown(
    """
    <style>
    .hero {background: linear-gradient(135deg,#4F46E5,#7C3AED); color:white;
           padding:28px 32px; border-radius:16px; margin-bottom:18px;}
    .hero h1 {color:white; margin:0 0 6px 0; font-size:2rem;}
    .hero p {margin:0; opacity:0.92;}
    .agent-card {border:1px solid #E5E7EB; border-radius:12px; padding:14px 16px;
                 background:#FFFFFF; min-height:92px;}
    .agent-name {font-weight:600; color:#1F2937;}
    .badge {display:inline-block; margin-top:8px; padding:3px 12px; border-radius:999px;
            font-size:0.82rem; font-weight:600;}
    .Pending {background:#F3F4F6; color:#4B5563;}
    .Working {background:#FEF3C7; color:#92400E;}
    .Completed {background:#D1FAE5; color:#065F46;}
    .Failed {background:#FEE2E2; color:#991B1B;}
    </style>
    """,
    unsafe_allow_html=True,
)

ICONS = {"Pending": "⏳", "Working": "⚙️", "Completed": "✅", "Failed": "❌"}
DESCRIPTIONS = {
    "Research Planner": "Plans the research questions",
    "Web Researcher": "Searches the web for evidence",
    "Research Analyst": "Finds key insights and gaps",
    "Report Writer": "Writes the final report",
}


def draw_status(placeholder, statuses):
    """Draw one card per agent with its real current status."""
    with placeholder.container():
        columns = st.columns(len(STEPS))
        for column, name, status in zip(columns, STEPS, statuses):
            column.markdown(
                f"""<div class="agent-card">
                <div class="agent-name">{ICONS[status]} {name}</div>
                <div style="color:#6B7280;font-size:0.85rem;">{DESCRIPTIONS[name]}</div>
                <span class="badge {status}">{status}</span></div>""",
                unsafe_allow_html=True,
            )


def friendly_error(error: Exception) -> str:
    text = str(error).lower()
    if "401" in text or "invalid api key" in text or "authentication" in text:
        return "Groq rejected the API key. Check GROQ_API_KEY in Streamlit Secrets."
    if "429" in text or "rate limit" in text or "rate_limit" in text:
        return "Groq rate limit reached. Wait a minute and try again, or try a narrower topic."
    if "model" in text and ("not found" in text or "does not exist" in text):
        return f"Groq could not find the model {MODEL_NAME}. Check the model name in config.py."
    return "Something went wrong while the agents were working. Details are below."


# ---------- Header ----------
st.markdown(
    f"""<div class="hero"><h1>🔎 AI Research Team</h1>
    <p>Four AI agents plan, search the web, analyze and write an evidence-based report.
    Model: {MODEL_NAME} on Groq.</p></div>""",
    unsafe_allow_html=True,
)

api_key = get_api_key()
if not api_key:
    st.error(
        "GROQ_API_KEY is missing. In Streamlit Cloud open App settings → Secrets "
        'and add:  GROQ_API_KEY = "your_key_here"'
    )

topic = st.text_input(
    "Research topic",
    placeholder="e.g. Impact of solar power adoption in Pakistan",
    max_chars=200,
)
start = st.button("🚀 Start Research", type="primary", use_container_width=True,
                  disabled=not api_key)

st.subheader("Live agent activity")
status_box = st.empty()
statuses = st.session_state.get("statuses", ["Pending"] * len(STEPS))
draw_status(status_box, statuses)

# ---------- Run ----------
if start:
    if len(topic.strip()) < 5:
        st.warning("Please enter a research topic (at least 5 characters).")
    else:
        statuses = ["Pending"] * len(STEPS)
        st.session_state.pop("result", None)
        st.session_state.pop("error", None)

        def on_status(index, status):
            statuses[index] = status
            draw_status(status_box, statuses)

        try:
            with st.spinner("The agents are working. This usually takes 1-3 minutes..."):
                st.session_state["result"] = run_research(topic.strip(), api_key, on_status)
                st.session_state["topic"] = topic.strip()
        except Exception as error:
            st.session_state["error"] = (friendly_error(error), repr(error))
        st.session_state["statuses"] = statuses

# ---------- Results ----------
if "error" in st.session_state:
    message, details = st.session_state["error"]
    st.error(message)
    with st.expander("Technical details"):
        st.code(details)

if "result" in st.session_state:
    result = st.session_state["result"]
    st.success("Research complete.")
    tab_report, tab_findings, tab_sources = st.tabs(
        ["📄 Report", "💡 Key findings", f"🔗 Sources ({len(result['sources'])})"]
    )
    with tab_report:
        st.markdown(result["report"])
        st.download_button(
            "⬇️ Download report (.md)",
            data=result["report"] + "\n\n## Sources\n" + "\n".join(
                f"- {s['title']} - {s['url']}" for s in result["sources"]),
            file_name="research_report.md",
            mime="text/markdown",
        )
    with tab_findings:
        st.markdown(result["findings"])
    with tab_sources:
        st.caption("These are the real search results the Web Researcher received.")
        if not result["sources"]:
            st.warning("No sources were collected. Treat the report with caution.")
        for s in result["sources"]:
            st.markdown(f"**[{s['title'] or s['url']}]({s['url']})**  \n{s['snippet']}")

st.caption("Reports are AI-generated from web search snippets. Verify important facts at the sources.")