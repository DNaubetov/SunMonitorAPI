import datetime
import uuid
from typing import List
from auth.authenticate import authenticate
from beanie import PydanticObjectId
from database.connection import Database
from fastapi import APIRouter, Depends, HTTPException, status

from models.api_key import ApiKey
from models.controllers import Controller, ControllerCreate
from models.users import User

"""
1. Нужно добавить ограничение по ролям!
2. Нужно добавить ручку для получения данных о инверторах, контроллером!
3. Нужно сделать защиту от дурака, что бы все вводилось в нижнем регистре
"""

controller_router = APIRouter(tags=["Controllers"])

controller_database = Database(Controller)


@controller_router.get("/", response_model=List[Controller],
                       summary="Ручка для получения всех контроллеров")
async def retrieve_all_controllers(user: str = Depends(authenticate)) -> List[Controller]:
    controllers = await controller_database.get_all()
    return controllers


@controller_router.get("/{controller_id}", response_model=Controller,
                       summary="Ручка для получения контроллера")
async def retrieve_controller(controller_id: PydanticObjectId, user: str = Depends(authenticate)) -> Controller:
    controller = await controller_database.get(controller_id)
    if not controller:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Контроллер с указанным идентификатором не существует"
        )
    return controller


@controller_router.post("/new", summary="Ручка создания контроллера")
async def create_controller(body: ControllerCreate, user: User = Depends(authenticate)) -> dict:
    """Нужно поставить ограничение по ролям, только админ может"""
    controller_exist = await Controller.find_one(Controller.name == body.name)
    if controller_exist:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Контроллер уже существует."
        )
    create_date = datetime.datetime.now(datetime.UTC)
    controller = Controller(
        name=body.name,
        location=body.location,
        connect=body.connect,
        create_date=create_date,
        creator=user.id)
    await controller_database.save(controller)

    create_api_key = ApiKey(
        name='Name Key',
        key=uuid.uuid4(),
        status=True,
        creator=user.id,
        create_date=create_date

    )
    await create_api_key.create()
    return {"message": "Контроллер создан успешно"}


@controller_router.put("/{id}", response_model=Controller,
                       summary="Ручка для редактирования контроллеров")
async def update_controller(controller_id: PydanticObjectId,
                            body: ControllerCreate, user: User = Depends(authenticate)) -> Controller:
    controller = await controller_database.get(controller_id)
    if controller.creator != user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь не допускается"
        )
    updated_controller = await controller_database.update(controller_id, body)
    if not updated_controller:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Контроллер с указанным идентификатором не существует"
        )
    return updated_controller


@controller_router.delete("/{id}", summary="Ручка для получение всех контроллеров")
async def delete_controller(controller_id: PydanticObjectId, user: str = Depends(authenticate)) -> dict:
    controller = await controller_database.get(controller_id)
    if not controller:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="контроллер не найден"
        )
    if controller.creator != user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Операция не разрешена"
        )
    await controller_database.delete(controller_id)

    return {
        "message": "Контроллер успешно удален."
    }
