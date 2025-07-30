from pydantic import BaseModel


class Job(BaseModel):
    classification: str
