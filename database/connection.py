from typing import Optional

from auth.hash_password import HashPassword
from models.api_key import ApiKey
from models.controllers import Controller
from models.events import Event
from models.invertors import Inverter
from models.received_data import AllData
from models.registers import Registers
from models.users import User, RoleEnum
from beanie import init_beanie, PydanticObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from pydantic_settings import BaseSettings

hash_password = HashPassword()


class Settings(BaseSettings):
    DATABASE_URL: Optional[str] = None
    SECRET_KEY: Optional[str] = None
    SUPER_ADMIN_LOG: Optional[str] = None
    SUPER_ADMIN_PASS: Optional[str] = None

    async def initialize_database(self):
        client = AsyncIOMotorClient(self.DATABASE_URL)
        await init_beanie(database=client.get_default_database(),
                          document_models=[User, Controller, Inverter, AllData, Registers, ApiKey])

        if not await User.find_one(User.role == RoleEnum.super_admin):
            hashed_password = hash_password.create_hash(self.SUPER_ADMIN_PASS)
            super_admin = User(
                name=self.SUPER_ADMIN_LOG,
                password=hashed_password,
                role=RoleEnum.super_admin
            )
            await super_admin.insert()
            print("Superuser created")

    class Config:
        # env_file = ".env"
        env_file = ".env.local"


class Database:
    def __init__(self, model):
        self.model = model

    async def save(self, document):
        await document.create()
        return

    async def add_list(self, documents: list):
        await self.model.insert_many(documents)

    async def get(self, id: PydanticObjectId):
        doc = await self.model.get(id)
        if doc:
            return doc
        return False

    async def get_all(self):
        docs = await self.model.find_all().to_list()
        return docs

    async def update(self, id: PydanticObjectId, body: BaseModel):
        doc_id = id
        des_body = body.dict()

        des_body = {k: v for k, v in des_body.items() if v is not None}
        update_query = {"$set": {
            field: value for field, value in des_body.items()
        }}

        doc = await self.get(doc_id)
        if not doc:
            return False
        await doc.update(update_query)
        return doc

    async def delete(self, id: PydanticObjectId):
        doc = await self.get(id)
        if not doc:
            return False
        await doc.delete()
        return True
