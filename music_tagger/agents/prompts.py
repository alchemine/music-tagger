"""Prompt templates."""

from pydantic import BaseModel
from langchain_core.messages import (
    BaseMessage,
    AIMessage,
    HumanMessage,
    ToolMessage,
)
from langchain_core.prompts import ChatPromptTemplate

from music_tagger.utils.utils import dedent


def get_system_prompt() -> str:
    return dedent(
        """
        --- Role ---
        You are a well-informed music critic. Your speciality is to extract information about songs.
        Return information about songs which includes the title and the artist.
        """
    )


def get_few_shot_system_prompt(name: str, title: str, artist: str | None) -> str:
    return dedent(
        """
        example_user: %s
        example_assistant: {{"title": "%s", "artist": "%s"}}
        """
        % (name, title, artist)
    )


def get_few_shot_system_prompts(examples: list[tuple[str, BaseModel]]) -> str:
    if examples:
        message = dedent(
            """
            --- Examples ---
            """
        )
        for name, info in examples:
            message += f"{get_few_shot_system_prompt(name, info.title, info.artist)}\n"
        return "\n" + dedent(message)
    else:
        return ""


def get_few_shot_tool_prompt(
    id: int, name: str, title: str, artist: str | None
) -> list[BaseMessage]:
    examples = [
        HumanMessage(name, name="example_user"),
        AIMessage(
            "",
            name="example_assistant",
            tool_calls=[
                {
                    "name": "joke",
                    "args": {"title": title, "artist": artist},
                    "id": str(id),
                }
            ],
        ),
        ToolMessage("", tool_call_id=str(id)),
    ]
    return examples


def get_few_shot_tool_prompts(examples: list[tuple[str, BaseModel]]) -> str:
    messages = []
    for id, (name, info) in enumerate(examples):
        messages += get_few_shot_tool_prompt(id, name, info.title, info.artist)
    return messages


def get_prompt_template(
    examples: list[tuple[str, BaseModel]], example_type: str
) -> str:
    if example_type == "system":
        return ChatPromptTemplate.from_messages(
            [
                ("system", get_system_prompt() + get_few_shot_system_prompts(examples)),
                ("human", "{input}"),
            ]
        )
    elif example_type == "tool":
        tool_messages = get_few_shot_tool_prompts(examples)
        return ChatPromptTemplate.from_messages(
            [
                ("system", get_system_prompt()),
                ("placeholder", "{examples}"),
                ("human", "{input}"),
            ]
        ).partial(examples=tool_messages)
    else:
        raise ValueError(f"Invalid example type: {example_type}")
