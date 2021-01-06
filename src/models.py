from typing import Optional, List

from pydantic import BaseModel


class Videos(BaseModel):
    id: str
    url: str
    description: str


class Playlist(BaseModel):
    id: Optional[str]
    url = str
    description = Optional[str]
    videos = List[Videos]

    class Config:
        arbitrary_types_allowed = True
