from decimal import Decimal

from pydantic import BaseModel, Field
from pydantic_extra_types.currency_code import Currency


class Wage(BaseModel):
    currency: Currency = 'USD'
    rate: Decimal = Field(max_digits=5, decimal_places=2, ge=0.0)
    fringe: Decimal = Field(max_digits=5, decimal_places=2, ge=0.0)
