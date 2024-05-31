"""Agent executor module."""

from pydantic import BaseModel

from music_tagger.agents.llm import get_llm
from music_tagger.agents.prompts import get_prompt_template
from music_tagger.agents.tool import RecordSong


def get_chain(examples: list[tuple[str, BaseModel]], example_type: str = "tool"):
    prompt_template = get_prompt_template(examples, example_type=example_type)
    structured_model = get_llm().with_structured_output(RecordSong)
    chain = prompt_template | structured_model
    return chain
