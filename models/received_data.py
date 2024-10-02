import datetime
from beanie import Document
from pydantic import BaseModel

from models.invertors import Serial_Number


class ReceivedStatus(BaseModel):
    data: str


class ReceivedData(ReceivedStatus):
    unit: str | None


class ListReceivedData(BaseModel):
    status: ReceivedStatus
    current_power: ReceivedData
    today_generate_energy: ReceivedData
    temperature: ReceivedData
    total_generate_energy: ReceivedData


class AllData(Document):
    serial_number: Serial_Number
    create_date: datetime.datetime = datetime.datetime.now(datetime.UTC)
    inverter_registers_data: ListReceivedData

    class Settings:
        name = "alldata"
