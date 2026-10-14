"""Settings shared by the whole project: API key lookup and the Groq LLM."""
import os

import streamlit as st
from crewai import LLM

# Groq's model id is literally "openai/gpt-oss-120b".
MODEL_NAME = "openai/gpt-oss-120b"
GROQ_BASE_URL = "https://api.groq.com/openai/v1"


def get_api_key() -> str:
    """Read the Groq key from Streamlit Secrets (or an environment variable)."""
    try:
        key = st.secrets["GROQ_API_KEY"]
    except Exception:
        key = os.getenv("GROQ_API_KEY", "")
    return str(key).strip()


def build_llm(api_key: str) -> LLM:
    """Create the Groq model for CrewAI.

    CrewAI 1.15 has no built-in "groq" provider, but Groq speaks the OpenAI
    protocol, so we use CrewAI's OpenAI provider and point it at Groq.
    """
    return LLM(
        model=MODEL_NAME,
        provider="openai",
        base_url=GROQ_BASE_URL,
        api_key=api_key,
        temperature=0.2,
        max_tokens=3000,
    )