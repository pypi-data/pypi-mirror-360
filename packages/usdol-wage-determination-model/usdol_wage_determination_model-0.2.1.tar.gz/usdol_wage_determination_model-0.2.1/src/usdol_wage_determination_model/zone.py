from pydantic import BaseModel, NonNegativeFloat, model_validator
from pydantic_extra_types.coordinate import Coordinate


class Zone(BaseModel):
    center: Coordinate
    radius_min: NonNegativeFloat = 0.0
    radius_max: NonNegativeFloat = float('inf')

    @model_validator(mode='after')
    def validate_radii(self):
        if self.radius_max <= self.radius_min:
            raise ValueError(f'Max radius of {self.radius_max} must be larger than min radius of {self.radius_min}')
        return self
