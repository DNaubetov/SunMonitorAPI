import datetime
import uuid
from typing import List

from auth.authenticate import authenticate
from beanie import PydanticObjectId
from database.connection import Database
from fastapi import APIRouter, Depends, HTTPException, status
from models.api_key import ApiKey, CreateApiKey
from models.users import User

api_key_router = APIRouter(
    tags=["Api key"]
)

api_key_database = Database(ApiKey)


@api_key_router.get("/", response_model=List[ApiKey])
async def retrieve_all_keys(user: str = Depends(authenticate)) -> List[ApiKey]:
    events = await api_key_database.get_all()
    return events


@api_key_router.get("/user", response_model=ApiKey)
async def retrieve_key(user: User = Depends(authenticate)) -> list[ApiKey]:
    key = await ApiKey.find(ApiKey.creator == user.id).to_list()
    if not key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Key with supplied ID does not exist"
        )
    return key


@api_key_router.post("/new")
async def create_key(body: CreateApiKey, user: User = Depends(authenticate)) -> dict:

    create_date = datetime.datetime.now(datetime.UTC)
    create_api_key = ApiKey(
        name=body.name,
        key=uuid.uuid4(),
        status=body.status,
        creator=user.id,
        create_date=create_date
    )
    await create_api_key.create()

    return {
        "message": "Event created successfully"
    }


@api_key_router.put("/{id}", response_model=CreateApiKey)
async def update_key(id: PydanticObjectId, body: CreateApiKey, user: User = Depends(authenticate)) -> ApiKey:
    key = await api_key_database.get(id)
    if key.creator != user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Operation not allowed"
        )
    key = await api_key_database.update(id, body)
    if not key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Api key with supplied ID does not exist"
        )
    return key


@api_key_router.put("/{id_key}/{api_status}", response_model=ApiKey)
async def switch_key_status(id_key: PydanticObjectId, api_status: bool, user: User = Depends(authenticate)) -> ApiKey:
    key = await ApiKey.find_one(ApiKey.id == id_key)
    if key.creator != user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Operation not allowed"
        )
    key.status = api_status
    await key.save()
    if not key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Api key with supplied ID does not exist"
        )
    return key


@api_key_router.delete("/{id}")
async def delete_key(id: PydanticObjectId, user: str = Depends(authenticate)) -> dict:
    key = await api_key_database.get(id)
    if not key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Api key not found"
        )
    if key.creator != user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Operation not allowed"
        )
    key = await api_key_database.delete(id)

    return {
        "message": "Api key deleted successfully."
    }