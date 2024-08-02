from enum import Enum

from beanie import Document

from pydantic import BaseModel, EmailStr, constr, field_validator


class RoleEnum(str, Enum):
    super_admin = 'super_admin'
    admin = 'admin'
    controller = 'controller'
    dispatcher = 'dispatcher'


class User(Document):
    name: constr(min_length=1, max_length=50)
    password: constr(min_length=1, max_length=100)
    role: RoleEnum = RoleEnum.dispatcher

    @field_validator('name')
    def convert_to_lower(cls, v: str) -> str:
        return v.lower()

    class Settings:
        name = "users"

    class Config:
        json_schema_extra = {
            "example": {
                "name": "fastapi@packt.com",
                "password": "strong!!!",
            }
        }


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
