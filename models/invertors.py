import datetime
from beanie import Document
from beanie import PydanticObjectId
from pydantic import BaseModel, constr, field_validator
from models.ops_registers import ReadRegistersListOPS
from models.registers import ReadRegistersList

Name_Inverter = constr(min_length=1, max_length=100)
Serial_Number = constr(min_length=1, max_length=100)
Registers_Name = constr(min_length=1, max_length=100)


class InverterForMC(BaseModel):
    """Данная моделька для МК, что бы получать данные!"""
    serial_number: Serial_Number
    slave: int
    registers: ReadRegistersList | ReadRegistersListOPS

    @field_validator('serial_number')
    def convert_to_lower(cls, v: str) -> str:
        return v.upper()


class InverterCreate(InverterForMC, BaseModel):
    name: Name_Inverter
    capacity: constr(min_length=1, max_length=100)
    registers: constr(min_length=1, max_length=100)
    controller: PydanticObjectId
    location: constr(min_length=1, max_length=100) = "АО ТЭС"

    @field_validator('location')
    def convert_to_lower(cls, v: str) -> str:
        return v.upper()


class Inverter(Document, InverterCreate):
    create_date: datetime.datetime = datetime.datetime.now(datetime.UTC)
    creator: PydanticObjectId

    class Settings:
        name = "inverters"
