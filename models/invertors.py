import datetime
from beanie import Document
from beanie import PydanticObjectId
from pydantic import BaseModel, constr, field_validator
from models.registers import ReadRegistersList

Name_Inverter = constr(min_length=1, max_length=100)
Serial_Number = constr(min_length=1, max_length=100)
Registers_Name = constr(min_length=1, max_length=100)


class InverterForMC(BaseModel):
    """Данная моделька для МК, что бы получать данные!"""
    serial_number: Serial_Number
    slave: int
    registers: ReadRegistersList

    @field_validator('serial_number')
    def convert_to_lower(cls, v: str) -> str:
        return v.upper()


class InverterCreate(InverterForMC, BaseModel):
    name: Name_Inverter
    capacity: constr(min_length=1, max_length=100)
    registers: constr(min_length=1, max_length=100)
    controller: PydanticObjectId


class Inverter(Document, InverterCreate):
    """Модель для хранения в бд
     capacity установленная мощность"""
    create_date: datetime.datetime = datetime.datetime.now(datetime.UTC)
    creator: PydanticObjectId

    # class Config:
    #     json_schema_extra = {
    #         "example": {
    #             "title": "FastAPI BookLaunch",
    #             "image": "https://linktomyimage.com/image.png",
    #             "description": "We will be discussing the contents of the FastAPI book in this event.Ensure to come with your own copy to win gifts!",
    #             "tags": ["python", "fastapi", "book", "launch"],
    #             "location": "Google Meet"
    #         }
    #     }
    #

    class Settings:
        name = "inverters"
