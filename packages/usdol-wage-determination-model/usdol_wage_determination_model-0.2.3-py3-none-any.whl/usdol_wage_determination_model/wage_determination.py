from datetime import date
from enum import StrEnum
from orjson import dumps

from pydantic import BaseModel, ConfigDict, Field, NonNegativeInt, model_validator

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
    model_config = ConfigDict(mode='json', exclude_none=True)

    decision_number: str = Field(pattern=r'^[A-Z]{2}[0-9]{8}$')
    modification_number: NonNegativeInt
    publication_date: date
    effective: DateRange
    active: bool
    construction_type: ConstructionType
    location: Location
    rate_identifier: str
    survey_date: date
    job: Job
    wage: Wage

    @model_validator(mode='after')
    def validate_dates(self):
        if self.effective.start_date < self.publication_date:
            raise ValueError(f'Effective start date of {self.effective.start_date} cannot be before ' +
                             f'publication date of {self.publication_date}')
        if self.survey_date > self.publication_date:
            raise ValueError(f'Survey completion date of {self.survey_date} cannot be after ' +
                             f'publication date of {self.publication_date}')
        return self

    def dump_json(self):
        return dumps(self.model_dump(mode='json', exclude_none=True))
