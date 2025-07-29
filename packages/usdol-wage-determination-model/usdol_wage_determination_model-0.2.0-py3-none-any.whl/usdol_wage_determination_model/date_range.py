from datetime import date

from pydantic import BaseModel, model_validator


class DateRange(BaseModel):
    start_date: date
    end_date: date = date.max

    @model_validator(mode='after')
    def validate_end(self):
        if self.end_date < self.start_date:
            raise ValueError(f'End date of {self.end_date} cannot be before start date of {self.start_date}')
        return self
