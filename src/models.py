from typing import Optional, List

from pydantic import BaseModel


class Videos(BaseModel):
    id: str
    url: str
    description: str = None


class Playlist(BaseModel):
    id: Optional[str] = None
    url: str
    user_id: int
    description: Optional[str]
    videos: List[Videos] = []
