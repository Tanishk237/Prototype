# LLM utility functions
from langchain_groq import ChatGroq
from src.config.settings import GROQ_API_KEY, GROQ_MODEL, TEMPERATURE


def get_llm():
    """Initialize and return a Groq LLM instance."""
    llm = ChatGroq(
        model=GROQ_MODEL,
        groq_api_key=GROQ_API_KEY,
        temperature=TEMPERATURE
    )

    return llm
