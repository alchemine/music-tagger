"""Music tagger class."""

from pydantic import BaseModel

from music_tagger.utils.config import LOG_PROMPT
from music_tagger.agents.chain import get_chain


class MusicTagger:
    def __init__(self, examples: list[tuple[str, BaseModel]], example_type: str):
        self.examples = examples
        self.example_type = example_type

    def build(self):
        self.chain = get_chain(self.examples, self.example_type)
        self.prompt = self.chain.steps[0]

    def run(self, input: str, log_prompt: bool = LOG_PROMPT):
        if log_prompt:
            self.log_prompt(input)
        return self.chain.invoke(input)

    def log_prompt(self, input: str):
        val = self.prompt.invoke(input).to_string()
        print(val)
        return val
