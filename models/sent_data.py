import datetime
from typing import List
from pydantic import BaseModel

from models.invertors import Serial_Number


class ChartData(BaseModel):
    data: float
    create_date: datetime.datetime | str


class SendChartData(BaseModel):
    description: str
    unit: str
    data_list: List[ChartData]


class SendChartDataAllInv(SendChartData):
    serial_number: Serial_Number
