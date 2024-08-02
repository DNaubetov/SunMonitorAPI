from pydantic import BaseModel, field_validator
import datetime


class DateRangeModel(BaseModel):
    start_date: datetime.date
    end_date: datetime.date

    @field_validator('start_date', 'end_date', mode='before')
    def check_date_range(cls, v):
        if not (datetime.date(2020, 1, 1) <= v <= datetime.date(2100, 12, 31)):
            raise ValueError('Date must be between 2020 and 2100')
        return v

    @field_validator('end_date')
    def check_dates(cls, v, values):
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v
