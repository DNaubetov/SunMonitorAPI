import datetime
from enum import Enum
from pydantic import BaseModel, constr, field_validator
from beanie import Document, PydanticObjectId

from models.ops_registers import ReadRegistersListOPS


class FunctionEnum(int, Enum):
    read_holding_registers = 3
    read_input_registers = 4


class CountEnum(int, Enum):
    bit16uint = 1
    bit32uint = 2
    bit64uint = 4
    bit16int = 11
    bit32int = 12
    bit64int = 14
    bit16float = 21
    bit32float = 22
    bit64float = 24
    bit_str = 31


class StatusRegister(BaseModel):
    function: FunctionEnum = FunctionEnum.read_input_registers
    address: int
    count: CountEnum


class Register(StatusRegister):
    coefficient: constr(min_length=1, max_length=10) | None
    unit: constr(min_length=1, max_length=100) | None


class ReadRegistersList(BaseModel):
    status: StatusRegister
    current_power: Register
    today_generate_energy: Register
    temperature: Register
    total_generate_energy: Register


class CreateRegisters(BaseModel):
    models: constr(min_length=1, max_length=100)
    registers_list: ReadRegistersList | ReadRegistersListOPS

    @field_validator('models')
    def convert_to_lower(cls, v: str) -> str:
        return v.upper()


class Registers(Document, CreateRegisters):
    create_date: datetime.datetime = datetime.datetime.now(datetime.UTC)
    creator: PydanticObjectId

    class Settings:
        collection = "registers"
