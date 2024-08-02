import datetime
from enum import Enum
from pydantic import BaseModel, constr, field_validator
from beanie import Document, PydanticObjectId


class FunctionEnum(int, Enum):
    read_holding_registers = 3
    read_input_registers = 4


class CountEnum(int, Enum):
    bit16 = 1
    bit32 = 2
    bit64 = 4


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
    work_time_total: Register


class CreateRegisters(BaseModel):
    models: constr(min_length=1, max_length=100)
    registers_list: ReadRegistersList

    @field_validator('models')
    def convert_to_lower(cls, v: str) -> str:
        return v.upper()


class Registers(Document, CreateRegisters):
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
        collection = "registers"


solax_x3_50k_tl = ReadRegistersList(
    temperature=Register(function=4, address=1, count=2, coefficient='0.1', unit='kwh'),
    status=Register(function=4, address=1, count=2, coefficient='0.1', unit='kwh'),
    current_power=Register(function=4, address=1, count=2, coefficient='0.1', unit='kwh'),
    today_generate_energy=Register(function=4, address=1, count=2, coefficient='0.1', unit='kwh'),
    total_generate_energy=Register(function=4, address=1, count=2, coefficient='0.1', unit='kwh'),
    work_time_total=Register(function=4, address=1, count=2, coefficient='0.1', unit='kwh'))
growatt_mid_30k = ReadRegistersList(
    temperature=Register(function=4, address=1, count=2, coefficient='0.1', unit='kwh'),
    status=Register(function=4, address=1, count=2, coefficient='0.1', unit='kwh'),
    current_power=Register(function=4, address=1, count=2, coefficient='0.1', unit='kwh'),
    today_generate_energy=Register(function=4, address=53, count=2, coefficient='0.1', unit='kwh'),
    total_generate_energy=Register(function=4, address=55, count=2, coefficient='0.1', unit='kwh'),
    work_time_total=Register(function=4, address=57, count=2, coefficient='0.5', unit='c'))



"""

{
  "models": "growatt_mid_30ktl3-x2",
  "registers_list": {
    "status": {
      "function": 4,
      "address": 0,
      "count": 1
    },
    "current_power": {
      "function": 4,
      "address": 1,
      "count": 2,
      "coefficient": "0.1",
      "unit": "w"
    },
    "today_generate_energy": {
      "function": 4,
      "address": 53,
      "count": 2,
      "coefficient": "0.1",
      "unit": "kwh"
    },
    "temperature": {
      "function": 4,
      "address": 93,
      "count": 1,
      "coefficient": "0.1",
      "unit": "C"
    },
    "total_generate_energy": {
      "function": 4,
      "address": 55,
      "count": 2,
      "coefficient": "0.1",
      "unit": "kwh"
    },
    "work_time_total": {
      "function": 4,
      "address": 57,
      "count": 2,
      "coefficient": "0.5",
      "unit": "s"
    }
  }
}

"""