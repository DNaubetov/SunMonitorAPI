import datetime
from beanie import Document, PydanticObjectId
from pydantic import BaseModel, field_validator, constr, IPvAnyAddress


class ConnectTCP(BaseModel):
    method: str = 'tcp'
    port: int = 512
    ip: IPvAnyAddress


class ConnectRTU(BaseModel):
    method: str = 'rtu'
    port: constr(min_length=1, max_length=100)
    baudrate: int
    parity: str
    stopbits: int
    bytesize: int
    timeout: int

    @field_validator('baudrate')
    @classmethod
    def validate_baudrate(cls, values: int) -> int:
        if values not in [1200, 2400, 4800, 9600, 19200, 38400]:
            raise ValueError('Скорость может быть только: 1200, 2400, 4800, 9600, 19200, 38400')
        return values


class ControllerCreate(BaseModel):
    name: constr(min_length=1, max_length=100)
    location: constr(min_length=1, max_length=100)
    connect: ConnectRTU | ConnectTCP

    @field_validator('name')
    def convert_to_lower(cls, v: str) -> str:
        return v.lower()


class Controller(Document, ControllerCreate):
    create_date: datetime.datetime = datetime.datetime.now(datetime.UTC)
    creator: PydanticObjectId

    class Settings:
        name = "controllers"
