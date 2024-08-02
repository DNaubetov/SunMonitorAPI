import datetime
from typing import List
from auth.authenticate import authenticate
from beanie import PydanticObjectId
from database.connection import Database
from fastapi import APIRouter, Depends, HTTPException, status
from models.registers import Registers, CreateRegisters
from models.users import User

"""
1. Нужно добавить ограничение по ролям!
2. Нужно добавить ручку для получения данных о инверторах, контроллером!
3. Нужно сделать защиту от дурака, что бы все вводилось в нижнем регистре
"""

register_router = APIRouter(tags=["Registers"])

register_database = Database(Registers)


@register_router.get("/", response_model=List[Registers],
                     summary="Ручка для получения всех registers")
async def retrieve_all_registers(user: str = Depends(authenticate)) -> List[Registers]:
    registers = await register_database.get_all()
    return registers


@register_router.get("/{id}", response_model=Registers,
                     summary="Ручка для получения register")
async def retrieve_register(register_id: PydanticObjectId, user: str = Depends(authenticate)) -> Registers:
    register = await register_database.get(register_id)
    if not register:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Register с указанным идентификатором не существует"
        )
    return register


@register_router.post("/new", summary="Ручка создания register")
async def create_register(body: CreateRegisters, user: User = Depends(authenticate)) -> dict:
    """Нужно поставить ограничение по ролям, только админ может"""
    register_exist = await Registers.find_one(Registers.models == body.models)
    if register_exist:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Register уже существует."
        )
    register = Registers(
        models=body.models,
        registers_list=body.registers_list,
        create_date=datetime.datetime.now(datetime.UTC),
        creator=user.id)
    await register_database.save(register)
    return {"message": "Registers создан успешно"}


@register_router.put("/{id}", response_model=Registers,
                     summary="Ручка для редактирования контроллеров")
async def update_register(register_id: PydanticObjectId,
                          body: CreateRegisters, user: str = Depends(authenticate)) -> Registers:
    register = await register_database.get(register_id)
    if register.creator != user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь не допускается"
        )
    updated_register = await register_database.update(register_id, body)
    if not updated_register:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Register с указанным идентификатором не существует"
        )
    return updated_register


@register_router.delete("/{id}", summary="Ручка для получение всех контроллеров")
async def delete_register(register_id: PydanticObjectId, user: str = Depends(authenticate)) -> dict:
    register = await register_database.get(register_id)
    if not register:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Register не найден"
        )
    if register.creator != user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Операция не разрешена"
        )
    await register_database.delete(register_id)

    return {
        "message": "Register успешно удален."
    }
