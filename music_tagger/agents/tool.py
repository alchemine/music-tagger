"""Tagging function."""

from pydantic import BaseModel, Field


class RecordSong(BaseModel):
    """Record some identifying information about a song."""

    title: str = Field(description="The song's title")
    # title_en: str = Field(description="The song's title (English)")
    # title_jp: str = Field(description="The song's title (Japanese)")
    # title_ko: str = Field(description="The song's title (Korean)")
    artist: str = Field(description="The song's artist", default="#")
    # artist_provided: bool = Field(
    #     description="Whether the song's artist is provided or not"
    # )
