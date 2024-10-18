import datetime
from typing import List
from pydantic import BaseModel, constr

from models.invertors import Serial_Number


class ChartData(BaseModel):
    data: float
    create_date: datetime.datetime | str


class SendChartData(BaseModel):
    description: str
    unit: str
    data_list: List[ChartData]


class SendChartDataAllInv(SendChartData):
    location: constr(min_length=1, max_length=100)
    serial_number: Serial_Number
