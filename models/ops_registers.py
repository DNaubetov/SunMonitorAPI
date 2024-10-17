from pydantic import BaseModel, constr, field_validator


class StatusRegisterOPS(BaseModel):
    registers: constr(min_length=1, max_length=100) | None


class RegisterOPS(StatusRegisterOPS):
    coefficient: constr(min_length=1, max_length=10) | None
    unit: constr(min_length=1, max_length=100) | None


class ReadRegistersListOPS(BaseModel):
    status: StatusRegisterOPS
    current_power: RegisterOPS
    today_generate_energy: RegisterOPS
    temperature: RegisterOPS
    total_generate_energy: RegisterOPS
