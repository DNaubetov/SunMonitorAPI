from pydantic import BaseModel, constr, field_validator


class SerialNumberModel(BaseModel):
    serial_number: constr(min_length=1, max_length=100)

    @field_validator('serial_number')
    def convert_to_lower(cls, v: str) -> str:
        return v.upper()
