from datetime import date
from enum import StrEnum

from pydantic import BaseModel, conset, Field, NonNegativeInt

from .date_range import DateRange
from .job import Job
from .location import Location
from .wage import Wage


class ConstructionType(StrEnum):
    building = 'building'
    highway = 'highway'
    heavy = 'heavy'
    residential = 'residential'


class WageDetermination(BaseModel):
    decision_number: str = Field(pattern=r'^[A-Z]{2}[0-9]{8}$')
    modification_number: NonNegativeInt
    publication_date: date
    effective: DateRange
    active: bool
    construction_types: conset(item_type=ConstructionType, min_length=1)
    location: Location
    rate_identifier: str
    survey_date: date
    job: Job
    wage: Wage
