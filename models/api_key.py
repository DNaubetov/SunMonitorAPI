import datetime
import uuid

from pydantic import BaseModel, constr, field_validator
from beanie import Document, PydanticObjectId


class CreateApiKey(BaseModel):
    name: constr(min_length=1, max_length=50) = 'Name Key'
    status: bool = True

    @field_validator('name')
    def convert_to_lower(cls, v: str) -> str:
        return v.lower()


class ApiKey(Document, CreateApiKey):
    key: uuid.UUID
    create_date: datetime.datetime = datetime.datetime.now(datetime.UTC)
    creator: PydanticObjectId

    class Settings:
        name = "api_key"

