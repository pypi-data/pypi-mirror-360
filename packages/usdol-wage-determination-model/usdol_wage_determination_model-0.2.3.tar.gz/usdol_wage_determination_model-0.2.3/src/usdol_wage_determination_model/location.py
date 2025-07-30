from pydantic import BaseModel

from .zone import Zone


class Location(BaseModel):
    state: str
    county: str
    zone: Zone = None
