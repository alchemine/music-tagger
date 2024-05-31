"""LLM model."""

from langchain_openai import ChatOpenAI

from music_tagger.utils.config import LLM_MODEL


def get_llm(model: str = LLM_MODEL) -> ChatOpenAI:
    """Get LLM model."""
    return ChatOpenAI(model=model)
